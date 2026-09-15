import asyncio
import os
import subprocess
import uuid
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.genai import types

SANDBOX_CLI = "/usr/local/gcp/bin/sandbox"
IS_LOCAL_MODE = not Path(SANDBOX_CLI).exists()
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "").strip()
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

app = FastAPI(title="Coffee Shop Manager AI Agent")
session_service = InMemorySessionService()
runner: Runner | None = None


def run_sandbox_process(args: list[str]):
    """Run a command through the Cloud Run sandbox when available."""
    if IS_LOCAL_MODE:
        command = args[2:] if args[:2] == ["do", "--"] else args
    else:
        command = [SANDBOX_CLI, *args]
    return subprocess.run(command, capture_output=True, text=True, timeout=30)


def execute_sandbox_command(command: str) -> str:
    """Execute a POSIX shell command in the Cloud Run sandbox."""
    try:
        result = run_sandbox_process(["do", "--", "/bin/sh", "-c", command])
        if result.returncode != 0:
            return (
                f"Execution failed (exit code {result.returncode}).\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )
        return result.stdout or "Command completed successfully with no output."
    except subprocess.TimeoutExpired:
        return "Execution failed: command timed out after 30 seconds."
    except Exception as exc:
        return f"Sandbox error: {exc}"


def get_sheets_service():
    from google.auth import default
    from googleapiclient.discovery import build

    credentials, _ = default(
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/cloud-platform",
        ]
    )
    return build("sheets", "v4", credentials=credentials, cache_discovery=False)


def read_spreadsheet_values(spreadsheet_id: str, range_name: str) -> str:
    """Read values from a Google Sheet range."""
    try:
        if not spreadsheet_id:
            return "Spreadsheet is not configured. Set SPREADSHEET_ID in Cloud Run."
        service = get_sheets_service()
        result = (
            service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        rows = result.get("values", [])
        return str(rows) if rows else "No data found in the specified range."
    except Exception as exc:
        return f"Read Error: {exc}"


def update_spreadsheet_values(
    spreadsheet_id: str, range_name: str, values: List[List[str]]
) -> str:
    """Update values in a Google Sheet range."""
    try:
        if not spreadsheet_id:
            return "Spreadsheet is not configured. Set SPREADSHEET_ID in Cloud Run."
        service = get_sheets_service()
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="USER_ENTERED",
                body={"values": values},
            )
            .execute()
        )
        return f"Successfully updated {result.get('updatedCells', 0)} cells in {range_name}."
    except Exception as exc:
        return f"Write Error: {exc}"


def create_spreadsheet_tab(spreadsheet_id: str, tab_name: str) -> str:
    """Create a Google Sheet tab if it does not already exist."""
    try:
        if not spreadsheet_id:
            return "Spreadsheet is not configured. Set SPREADSHEET_ID in Cloud Run."
        service = get_sheets_service()
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        existing = {
            sheet.get("properties", {}).get("title")
            for sheet in spreadsheet.get("sheets", [])
        }
        if tab_name in existing:
            return f"Sheet tab '{tab_name}' already exists."

        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={"requests": [{"addSheet": {"properties": {"title": tab_name}}}]},
        ).execute()
        return f"Successfully created sheet tab '{tab_name}'."
    except Exception as exc:
        return f"Error creating sheet tab: {exc}"


def build_runner() -> Runner:
    """Build the ADK runner lazily so the web UI can always start."""
    global runner
    if runner is not None:
        return runner

    spreadsheet_context = SPREADSHEET_ID or "NOT_CONFIGURED"
    root_agent = LlmAgent(
        name="coffee_shop_manager_agent",
        description="AI business analyst for a coffee shop during university graduation weekend.",
        model=MODEL_NAME,
        instruction=(
            "You are an expert AI Business Analyst for a coffee shop during university graduation weekend.\n"
            f"The configured Google Spreadsheet ID is: {spreadsheet_context}.\n\n"
            "Workflow:\n"
            "1. Read historical POS data from the POS-2025 sheet tab when spreadsheet access is configured.\n"
            "2. Use the graduation schedule supplied by the manager to predict demand spikes and bottlenecks.\n"
            "3. Use the sandbox tool to write/run Python analysis when useful.\n"
            "4. If predicted wait time is above 10 minutes, diagnose whether the bottleneck is cashier capacity or barista output.\n"
            "5. Present only 2-3 important findings and actionable staffing/inventory recommendations.\n"
            "6. Ask for explicit approval before changing any spreadsheet data.\n"
            "7. After approval, create TODO-2026 if needed and write approved tasks under Task, Category, Ceremony, Date_Added.\n"
            "Never claim that a spreadsheet was updated unless the update tool succeeds."
        ),
        tools=[
            FunctionTool(func=execute_sandbox_command),
            FunctionTool(func=read_spreadsheet_values),
            FunctionTool(func=update_spreadsheet_values),
            FunctionTool(func=create_spreadsheet_tab),
        ],
    )

    adk_app = App(name="coffee_shop_manager_app", root_agent=root_agent)
    runner = Runner(
        app=adk_app,
        session_service=session_service,
        auto_create_session=True,
    )
    return runner


async def run_agent(prompt: str, session_id: str) -> str:
    current_runner = build_runner()
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    chunks: list[str] = []

    async for event in current_runner.run_async(
        user_id="web_user",
        session_id=session_id,
        new_message=message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    chunks.append(part.text)

    return "".join(chunks).strip() or "Agent completed the request without a text response."


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "coffee-shop-manager-agent",
        "model": MODEL_NAME,
        "sandbox": not IS_LOCAL_MODE,
        "spreadsheet_configured": bool(SPREADSHEET_ID),
    }


@app.post("/chat")
async def chat_with_agent(payload: "UserPrompt"):
    if not payload.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    try:
        session_id = payload.session_id or str(uuid.uuid4())
        response = await run_agent(payload.prompt.strip(), session_id)
        return {"status": "success", "session_id": session_id, "response": response}
    except Exception as exc:
        print(f"Agent request failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Agent request failed: {exc}")


class UserPrompt(BaseModel):
    prompt: str
    session_id: str | None = None


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = str(uuid.uuid4())
    await websocket.send_text("🔌 Connected. Coffee Shop Manager Agent is ready.")

    try:
        while True:
            prompt = await websocket.receive_text()
            if not prompt.strip():
                continue
            await websocket.send_text("_Agent is analyzing the request..._")
            try:
                response = await run_agent(prompt.strip(), session_id)
                await websocket.send_text(response)
            except Exception as exc:
                print(f"WebSocket agent error: {exc}")
                await websocket.send_text(
                    "I hit an error while processing that request. "
                    "Please check the Cloud Run configuration and try again."
                )
    except WebSocketDisconnect:
        pass


@app.get("/", response_class=HTMLResponse)
async def get_chat_ui():
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Coffee Shop Manager AI Agent</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f7f4f1;color:#2f211d;height:100vh;display:flex}.sidebar{width:270px;background:#3e2723;color:#f7eee9;padding:28px 22px;display:flex;flex-direction:column}.logo{font-size:42px}.sidebar h1{font-size:21px;margin:12px 0 8px}.sidebar p{font-size:14px;line-height:1.6;color:#d7c7c0}.status{margin-top:auto;padding:12px;border:1px solid #67473e;border-radius:12px;font-size:13px}.dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:#8bc34a;margin-right:7px}.main{flex:1;display:flex;flex-direction:column;min-width:0}.top{padding:20px 28px;border-bottom:1px solid #e1d8d2;background:#fff}.top strong{font-size:18px}.top span{display:block;color:#7b6b64;font-size:13px;margin-top:3px}.chat{flex:1;overflow:auto;padding:28px}.messages{max-width:900px;margin:auto}.message{max-width:82%;padding:14px 16px;border-radius:15px;margin:0 0 14px;line-height:1.55;white-space:pre-wrap}.agent{background:#fff;border:1px solid #e5ddd8;box-shadow:0 2px 8px rgba(50,30,20,.04)}.user{background:#6d4c41;color:#fff;margin-left:auto}.composer{padding:18px 28px;background:#fff;border-top:1px solid #e1d8d2}.form{max-width:900px;margin:auto;display:flex;gap:10px}.form input{flex:1;padding:14px 16px;border:1px solid #d8cec8;border-radius:12px;font-size:15px;outline:none}.form input:focus{border-color:#8d6e63}.form button{border:0;border-radius:12px;padding:0 22px;background:#6d4c41;color:#fff;font-weight:700;cursor:pointer}.form button:disabled{opacity:.55;cursor:not-allowed}.hint{max-width:900px;margin:8px auto 0;color:#8a7b74;font-size:12px}@media(max-width:700px){.sidebar{display:none}.chat{padding:16px}.top,.composer{padding:14px 16px}.message{max-width:94%}}
</style>
</head>
<body>
<aside class="sidebar"><div class="logo">☕</div><h1>Coffee Shop Manager</h1><p>An AI agent for operational analysis, staffing recommendations and inventory planning.</p><div class="status"><span class="dot"></span>Cloud Run Agent</div></aside>
<main class="main"><header class="top"><strong>Manager Assistant</strong><span>Powered by Google ADK + Gemini</span></header><section class="chat"><div id="messages" class="messages"><div class="message agent">👋 Hi! I’m your Coffee Shop Manager AI Agent.\n\nShare a graduation schedule or ask me to analyze the coffee shop’s operational data.</div></div></section><footer class="composer"><div class="form"><input id="prompt" placeholder="Ask the manager agent something..." autocomplete="off"><button id="send">Send</button></div><div class="hint">Try: “Review last year’s POS data and identify staffing bottlenecks.”</div></footer></main>
<script>
const messages=document.getElementById('messages'),input=document.getElementById('prompt'),send=document.getElementById('send');
function add(text,cls){const el=document.createElement('div');el.className='message '+cls;el.textContent=text;messages.appendChild(el);document.querySelector('.chat').scrollTop=document.querySelector('.chat').scrollHeight;return el}
async function sendPrompt(){const prompt=input.value.trim();if(!prompt)return;add(prompt,'user');input.value='';send.disabled=true;const loading=add('Thinking...','agent');try{const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt})});const data=await r.json();loading.remove();add(data.response||data.detail||'No response returned.','agent')}catch(e){loading.remove();add('Unable to reach the agent. Please try again in a moment.','agent')}finally{send.disabled=false;input.focus()}}
send.addEventListener('click',sendPrompt);input.addEventListener('keydown',e=>{if(e.key==='Enter')sendPrompt()});
</script>
</body>
</html>
"""
    )
