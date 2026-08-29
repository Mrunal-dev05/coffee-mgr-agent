# Coffee Shop Inventory Agent

An AI-powered business analysis agent for a coffee shop that analyzes historical Point-of-Sale (POS) data to identify demand patterns, detect operational bottlenecks, and recommend staffing and inventory adjustments for university graduation weekend.

## Overview

The Coffee Shop Inventory Agent uses Google ADK and Gemini to analyze historical sales data stored in Google Sheets.

The agent:

- Reads historical POS data from Google Sheets
- Analyzes beverage demand and wait-time patterns
- Correlates demand patterns with graduation ceremony schedules
- Identifies potential staffing bottlenecks
- Recommends inventory and staffing adjustments
- Uses a human-in-the-loop approval workflow before modifying the TODO list
- Creates and updates a `TODO-2026` spreadsheet tab after explicit manager approval
- Runs as a deployed application on Google Cloud Run

## Problem

University graduation weekends can create sudden spikes in coffee-shop demand.

Without analyzing historical POS data, managers may:

- Understaff busy periods
- Experience long customer wait times
- Run short on high-demand ingredients
- Assign staff inefficiently

This agent turns historical POS data into actionable operational recommendations.

## How It Works

```text
Historical POS Data
        |
        v
   Google Sheets
        v
    AI Agent
   (Google ADK)
        |
        v
  Gemini Analysis
        |
        +------------------+
        |                  |
        v                  v
Demand Patterns      Bottleneck Analysis
        |                  |
        +--------+---------+
                 |
                 v
        Staffing & Inventory
          Recommendations
                 |
                 v
        Human Approval
                 |
          +------+------+
          |             |
         No            Yes
          |             |
       No change       TODO-2026
                       Update

## Technology Stack

* Python
* Google ADK (Agent Development Kit)
* Gemini
* Google Sheets API
* Google Cloud Run
* Google Cloud authentication
* FastAPI
* Docker

## Google Cloud Services

The application uses:

* Google Cloud Run for deployment
* Google Sheets API for POS and TODO data
* Google Vertex AI / Gemini for agent reasoning
* Google Cloud service account authentication

## Agent Workflow

### 1. Historical Data Analysis

The agent reads POS data from the spreadsheet and analyzes:

* Drip Coffee
* Cold Brew
* Extra Espresso
* Alternative Milk usage
* Pastry demand
* Number of cashiers
* Wait times

### 2. Ceremony-Based Analysis

The manager provides the current graduation ceremony schedule.

The agent compares the schedule with historical demand patterns to identify relevant high-demand periods.

### 3. Bottleneck Detection

The agent applies operational rules to identify potential bottlenecks.

For example:

* Wait time greater than 10 minutes
* Fewer than 2 cashiers → recommend an additional cashier
* 2 cashiers with complex beverage demand → identify barista capacity as the likely bottleneck

### 4. Human-in-the-Loop Approval

The agent does not immediately modify the spreadsheet.

It first presents:

* Data findings
* Bottleneck diagnosis
* Staffing recommendations
* Inventory recommendations

The manager must explicitly approve the proposed tasks.

### 5. TODO-2026 Update

After approval, the agent verifies whether the `TODO-2026` sheet tab exists.

If necessary, it creates the tab and adds approved tasks using:

* Task
* Category
* Ceremony
* Date_Added

## Example Analysis

A historical POS analysis identified a Saturday 6:00 PM bottleneck:

* Wait time: 12 minutes
* Cashiers working: 2
* Alt Milk usage: 190 oz
* Cold Brew: 40

Because two cashiers were already working while complex beverage demand was unusually high, the agent diagnosed the likely bottleneck as barista capacity.

Recommended action:

**Schedule a Support Barista during the Saturday evening peak and increase Alt Milk inventory.**

## Human-in-the-Loop Safety

Spreadsheet modifications require explicit manager approval.

The agent follows this workflow:

Analyze → Recommend → Ask for Approval → Update Spreadsheet 

This prevents the agent from making operational changes without human confirmation.

## Deployment

The application is deployed on Google Cloud Run.

### Live Application

[https://coffee-mgr-agent-bq2o3alxoa-el.a.run.app](https://coffee-mgr-agent-bq2o3alxoa-el.a.run.app)

### Source Code

[https://github.com/Mrunal-dev05/coffee-mgr-agent](https://github.com/Mrunal-dev05/coffee-mgr-agent)

## Project Structure

coffee-mgr-agent/
├── main.py
├── Dockerfile
├── requirements.txt
├── .gitignore
└── README.md


## Future Improvements

Potential future improvements include:

* More advanced demand forecasting
* Automated inventory quantity forecasting
* Historical trend visualization
* Integration with additional POS systems
* Multi-location coffee shop support
* Automated alerts for predicted bottlenecks

