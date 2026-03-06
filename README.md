<p align="center">
  <h1 align="center">🚀 CampaignX</h1>
  <p align="center"><strong>AI Multi-Agent Marketing Intelligence Platform</strong></p>
  <p align="center">
    <em>Fully Autonomous Campaign Strategy · Multi-Armed Bandit Optimization · Real-Time Agent Reasoning</em>
  </p>
</p>

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Why Multi-Agent Architecture?](#2-why-multi-agent-architecture)
3. [Project Structure](#3-project-structure)
4. [Agent Execution Pipeline](#4-agent-execution-pipeline)
5. [Multi-Agent Details (The 8 Agents)](#5-multi-agent-details-the-8-agents)
6. [Core Technical Innovations](#6-core-technical-innovations)
    - [Dynamic API Discovery](#dynamic-api-discovery)
    - [Multi-Armed Bandit (MAB) Optimization](#multi-armed-bandit-mab-optimization)
    - [Historical Learning Service](#historical-learning-service)
7. [Explainable AI & Transparent Logging](#7-explainable-ai--transparent-logging)
8. [Tech Stack](#8-tech-stack)
9. [Setup & Installation](#9-setup--installation)

---

## 1. Project Overview

**CampaignX** is an industrial-grade AI multi-agent system designed for the InXiteOut FrostHack 2026. It automates the entire lifecycle of email marketing campaigns—from natural language brief parsing to autonomous optimization. 

Built specifically for **SuperBFSI** (a premier Indian BFSI provider), the system manages complex financial marketing workflows using a cluster of 8 specialized agents that collaborate, reason, and execute against remote APIs discovered dynamically via OpenAPI standards.

---

## 2. Why Multi-Agent Architecture?

Instead of a monolithic LLM prompt, CampaignX uses an **Agentic Mesh Interface**:
*   **Modular Reasoning:** Each agent (e.g., `SegmentationAgent`, `StrategyAgent`) has a bounded context and validated Pydantic output.
*   **Sequential Reliability:** Data flows through a structured pipeline where each stage is verified before physical execution.
*   **Autonomous Optimization:** Independent `Optimization` and `Analytics` agents allow for programmatic learning loops without human intervention.
*   **Enterprise Transparency:** Every reasoning step, LLM call, and API interaction is logged with human-readable justifications.

---

## 3. Project Structure

```text
campaignx/
├── backend/
│   ├── agents/                 # Specialized AI Agent implementations 
│   │   ├── base_agent.py       # Core LLM & tool-calling interface
│   │   ├── campaign_brief_agent.py
│   │   ├── segmentation_agent.py
│   │   ├── strategy_agent.py
│   │   ├── content_agent.py
│   │   ├── execution_agent.py
│   │   ├── analytics_agent.py
│   │   ├── optimization_agent.py
│   │   └── insight_agent.py
│   ├── api/                    # FastAPI route definitions
│   ├── orchestrator/           # AgentOrchestrator: The brain of the pipeline
│   ├── services/               # Business logic & DB interaction
│   │   ├── historical_learning_service.py # Cross-campaign memory
│   │   ├── optimization_service.py        # MAB logic storage
│   ├── tools/                  # Dynamic API discovery tools
│   │   ├── openapi_loader.py   # OpenAPI spec parser
│   │   └── dynamic_tool_registry.py # Real-time API executor
│   ├── models.py               # SQLAlchemy ORM schemas
│   ├── schemas.py              # Pydantic validation schemas
│   └── main.py                 # FastAPI application entry point
├── frontend/
│   ├── src/
│   │   ├── pages/              # React page components (Dashboard, Logs, etc.)
│   │   ├── components/         # Reusable UI elements (Charts, Stats)
│   │   └── App.jsx             # Main router & layout
│   └── package.json
└── openapi.json                # Source of truth for remote API discovery
```

---

## 4. Agent Execution Pipeline

The orchestrator manages a bidirectional flow of data across two primary phases:

### Phase A: Strategic Planning (Human-in-the-Loop)
`Brief Parser` → `Segmentation` → `Strategy Designer` → `Content Generator` → **[APPROVAL GATE]**

### Phase B: Autonomous Execution & Optimization
`API Execution` → `Metric Retrieval` → `MAB Optimization Loop` → `Insight Generation`

---

## 5. Multi-Agent Details (The 8 Agents)

| Agent | Core Logic | Technical Output |
|-------|------------|------------------|
| **CampaignBriefAgent** | NLP parsing of complex marketing goals. | `BriefOutputSchema` |
| **SegmentationAgent** | Clustered retrieval from real API cohorts. | `SegmentationRulesSchema` |
| **StrategyAgent** | Temporal planning (Send Time) & A/B structures. | `StrategyOutputSchema` |
| **ContentAgent** | Personalized copy generation for segments. | `ContentVariantsSchema` |
| **ExecutionAgent** | Direct HTTP execution via Dynamic Tool Registry. | `api_calls_executed` log |
| **AnalyticsAgent** | Scrapes remote API for real CTR/Open rates. | `PerformanceMetric` units |
| **OptimizationAgent** | Applies Multi-Armed Bandit (MAB) logic. | `OptimizationDecisionSchema` |
| **InsightAgent** | Synthesizes metrics into human strategy. | `InsightsOutputSchema` |

---

## 6. Core Technical Innovations

### Dynamic API Discovery
No API endpoints are hardcoded. The platform uses `OpenAPILoader` to:
1.  Parse `openapi.json` at startup.
2.  Map methods (GET/POST) and paths to OpenAI Function schemas.
3.  Register endpoints in `DynamicToolRegistry`.
4.  Allow `ExecutionAgent` to call tools abstractly: `self.tool_registry.execute("send_campaign", args)`.

### Multi-Armed Bandit (MAB) Optimization
The `OptimizationAgent` implements a reinforcement learning loop that evaluates campaign variants using a proprietary **Weighted Engagement Formula**:

$$Score = (0.7 \times ClickRate) + (0.3 \times OpenRate)$$

*   **Exploit:** Allocates more traffic to variants with higher scores.
*   **Explore:** Modifies underperforming variants (Subject, Emoji, Tone) to discover better engagement peaks.
*   **Convergence:** The loop terminates early if any variant exceeds a **15% click rate** threshold.

### Historical Learning Service
System-wide intelligence is achieved via the `HistoricalLearningService`.
*   **Memory Injection:** Successful insights from Campaign N are retrieved and injected into the system prompt for Campaign N+1.
*   **Pattern Recognition:** The LLM analyzes cross-campaign data to identify high-conversion subject line patterns and send-time preferences for specific micro-segments.

---

## 7. Explainable AI & Transparent Logging

Transparency is built into the core:
*   **Agent Logs:** A live feed of every agent's "Reasoning Summary," exposing why specific segments or variants were chosen.
*   **Input/Output Visibility:** See the exact JSON payloads validated by Pydantic.
*   **API Interception:** Every dynamic API call is captured with its full HTTP shape (Headers, Body, Response).

---

## 8. Tech Stack

- **Backend:** FastAPI, SQLAlchemy, HTTPx, Pydantic v2.
- **LLM Engine:** Google Gemini 2.0 Flash (Reasoning) & Llama 3 (Optimization).
- **Frontend:** React 18, Vite, TailwindCSS, Recharts (for MAB visualization).
- **Database:** SQLite (Local Caching & History).

---

## 9. Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Add your GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

> **Note:** If port `5173` is in use, the frontend will automatically switch to `5174`. The backend is pre-configured to handle CORS for both origins.
