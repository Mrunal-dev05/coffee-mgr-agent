# ☕ Coffee Shop Manager AI Agent

> An AI-powered operations assistant that turns historical coffee-shop POS data into actionable staffing, inventory, and peak-demand recommendations.

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google ADK](https://img.shields.io/badge/Google%20ADK-2.8.0-4285F4?logo=google&logoColor=white)](https://google.github.io/adk-docs/)
[![Gemini](https://img.shields.io/badge/Gemini-AI-8E75B2?logo=google-gemini&logoColor=white)](https://ai.google.dev/)

## 🚀 Live Demo

**Try the deployed application:**

👉 https://coffee-shop-manager-agent.onrender.com

> The live demo is hosted on a free cloud instance and may take a few seconds to wake up after inactivity.

---

## 📌 Overview

Coffee shops near university campuses can experience sudden demand spikes during events such as graduation ceremonies. This project uses an AI agent to analyze historical Point-of-Sale (POS) data and help managers prepare for those peaks.

Instead of simply generating a response, the agent follows an operational workflow:

```text
Historical POS Data
        ↓
   Google Sheets
        ↓
   AI Agent (ADK)
        ↓
 Gemini Reasoning
        ↓
Demand + Bottleneck Analysis
        ↓
Staffing & Inventory Recommendations
        ↓
 Human Approval
        ↓
   TODO-2026 Update
```

The key idea is **human-in-the-loop automation**: the agent can analyze and recommend, but spreadsheet changes require explicit manager approval.

---

## ✨ What the Agent Can Do

- 📊 Analyze historical POS data
- ☕ Identify beverage and pastry demand patterns
- ⏱️ Detect periods with high customer wait times
- 👥 Analyze cashier and barista capacity
- 🎓 Compare demand patterns with graduation schedules
- 📦 Recommend inventory adjustments
- 🧑‍💼 Recommend staffing changes
- ✅ Ask for explicit approval before making operational changes
- 📝 Create/update a `TODO-2026` Google Sheets tab after approval
- 💬 Provide an interactive web interface through FastAPI

---

## 🧠 Example Scenario

Suppose historical data shows a Saturday 6:00 PM peak with:

| Metric | Observation |
|---|---:|
| Wait time | 12 minutes |
| Cashiers | 2 |
| Alternative milk | 190 oz |
| Cold brew | 40 |

The agent can reason that the main bottleneck is likely **barista capacity**, rather than checkout capacity, because two cashiers are already available while complex beverage demand is unusually high.

### Recommended action

> Schedule a support barista during the Saturday evening peak and increase alternative-milk inventory.

The manager can then approve or reject the recommendation.

---

## 🔐 Human-in-the-Loop Design

The agent intentionally separates **analysis** from **execution**.

```text
Analyze
   ↓
Recommend
   ↓
Ask Manager for Approval
   ↓
 ┌───────────────┐
 │               │
No              Yes
│               │
↓               ↓
No Change   Update TODO-2026
```

This prevents the agent from silently modifying operational data and makes the workflow safer for real-world use.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11 |
| API / Backend | FastAPI |
| Agent Framework | Google ADK |
| AI Model | Gemini |
| Data | Google Sheets API |
| Authentication | Google Cloud / Application Default Credentials |
| Frontend | HTML, CSS, JavaScript |
| Container Support | Docker |

---

## 🏗️ Architecture

```text
                    ┌─────────────────────┐
                    │   Manager / User    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   FastAPI Web UI    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Google ADK Agent  │
                    └───────┬─────┬───────┘
                            │     │
                 ┌──────────┘     └──────────┐
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ Gemini Reasoning│         │ Google Sheets   │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 └────────────┬──────────────┘
                              ▼
                    ┌─────────────────────┐
                    │ Recommendations +   │
                    │ Human Approval      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   TODO-2026 Tab     │
                    └─────────────────────┘
```

---

## 📂 Project Structure

```text
coffee-mgr-agent/
│
├── main.py            # FastAPI app + AI agent + tools
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container configuration
├── .gitignore
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mrunal-dev05/coffee-mgr-agent.git
cd coffee-mgr-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

**Windows:**

```bash
.venv\Scripts\activate
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini / Google Cloud credentials

Set up the required Google authentication for your environment before using Gemini and Google Sheets features.

### 5. Run the application

```bash
uvicorn main:app --reload
```

Then open:

```text
http://localhost:8000
```

Health check:

```text
http://localhost:8000/health
```

---

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Web interface |
| `/health` | GET | Service health check |
| `/chat` | POST | Send a message to the agent |
| `/ws` | WebSocket | Interactive real-time communication |

---

## 📈 Operational Logic

The agent focuses on practical signals from historical POS data, including:

- Drip coffee demand
- Cold brew demand
- Extra espresso usage
- Alternative milk usage
- Pastry demand
- Number of cashiers
- Customer wait times
- Graduation ceremony timing

These signals are combined to identify likely demand peaks and operational bottlenecks.

---

## 🎯 Why This Project Matters

This project demonstrates more than a basic chatbot. It combines:

- **Agentic AI** for reasoning and tool use
- **Real business data** through Google Sheets
- **Operational decision support** for staffing and inventory
- **Human approval** before state-changing actions
- **API + web interface** for practical usage
- **Cloud deployment** for a publicly accessible application

The goal is to show how an AI agent can move from **"answering questions"** to **"analyzing data, making recommendations, and safely assisting with business operations."**

---

## 🔮 Future Improvements

- 📊 Historical demand dashboards
- 🔮 Automated demand forecasting
- 📦 Quantity-level inventory forecasting
- 🚨 Proactive alerts for predicted bottlenecks
- 🏪 Multi-location coffee-shop support
- 🔌 Integration with additional POS systems
- 📅 Automatic event-calendar integration
- 📱 Responsive mobile-first interface

---

## 👩‍💻 Author

**Mrunal Pimpale**  
Computer Engineering Student | Software & AI Enthusiast

GitHub: https://github.com/Mrunal-dev05

---

## 📄 License

This project is intended for learning, experimentation, and portfolio demonstration.
