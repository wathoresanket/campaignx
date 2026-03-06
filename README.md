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
2. [Problem Statement](#2-problem-statement)
3. [System Architecture](#3-system-architecture)
4. [Multi-Agent Architecture](#4-multi-agent-architecture)
5. [Detailed Agent Explanations](#5-detailed-agent-explanations)
6. [Optimization Loop](#6-optimization-loop-explanation)
7. [Dynamic API Discovery](#7-dynamic-api-discovery)
8. [Intelligence Features](#8-intelligence-features)
9. [Segment Intelligence](#9-segment-intelligence)
10. [Historical Campaign Learning](#10-historical-campaign-learning)
11. [Optimization Timeline Visualization](#11-optimization-timeline-visualization)
12. [Campaign Lifecycle Timeline](#12-campaign-lifecycle-timeline)
13. [Live Agent Activity Feed](#13-live-agent-activity-feed)
14. [Tech Stack](#14-tech-stack)
15. [Database Schema](#15-database-schema)
16. [API Reference](#16-api-reference)
17. [Project Structure](#17-project-structure)
18. [Setup Instructions](#18-setup-instructions)
19. [Environment Variables](#19-environment-variables)
20. [Demo Walkthrough](#20-demo-walkthrough)
21. [Example Campaign Scenario](#21-example-campaign-scenario)
22. [Example AI Insights Output](#22-example-ai-insights-output)
23. [Design Decisions](#23-design-decisions)
24. [Troubleshooting](#24-troubleshooting)
25. [Future Improvements](#25-future-improvements)

---

## 1. Project Overview

**CampaignX** is an AI-powered multi-agent marketing automation platform that transforms a simple natural language campaign brief into a fully optimized, executed, and analyzed email marketing campaign — all with minimal human intervention.

The platform orchestrates **8 specialized AI agents** that collaborate in a pipeline:

1. **Parse** the campaign brief into structured data
2. **Segment** customers into micro-groups using real cohort data
3. **Strategize** send timing and A/B testing plans (informed by historical learnings)
4. **Generate** personalized email variants per segment (informed by historical learnings)
5. **Await** human-in-the-loop approval
6. **Execute** campaigns via the real CampaignX API
7. **Analyze** real engagement metrics (open/click rates from API reports)
8. **Optimize** using Multi-Armed Bandit algorithms (up to 3 loops)
9. **Generate** actionable marketing insights

The system also features **intelligence layers** including segment intelligence interpretation, historical campaign learning, optimization progress visualization, campaign lifecycle tracking, and live agent reasoning transparency.

---

## 2. Problem Statement

Modern marketing teams face several challenges:

- **Manual Campaign Planning**: Marketers spend hours manually crafting strategies, segmenting audiences, and writing copy
- **No Systematic Optimization**: A/B testing is often ad-hoc with no automated learning loop
- **Siloed Knowledge**: Insights from past campaigns are lost and not fed into future decisions
- **Lack of Transparency**: AI-assisted tools rarely show their reasoning, making them black boxes
- **Scalability**: Running personalized campaigns across multiple segments doesn't scale with manual processes

**CampaignX solves these problems** by providing an end-to-end autonomous marketing pipeline where AI agents collaborate, learn from past campaigns, and transparently show their reasoning at every step.

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        React + Vite Frontend                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │Campaign  │ │Approval  │ │Dashboard │ │Agent Logs│ │Historical│ │
│  │Brief Page│ │  Page    │ │  Page    │ │  Page    │ │ Learning │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ │
│       └─────────────┴─────────────┴─────────────┴─────────────┘     │
│                            Axios HTTP Client                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ REST API
┌────────────────────────────────┴────────────────────────────────────┐
│                        FastAPI Backend                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Agent Orchestrator                         │    │
│  │  Brief → Segment → Strategy → Content → [Approval Gate]     │    │
│  │  → Execution → Analytics → Optimization → Insights          │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                   Services Layer                             │    │
│  │  Campaign · Analytics · Optimization · Insight               │    │
│  │  Segment Intelligence · Historical Learning                  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │           SQLAlchemy ORM + SQLite / PostgreSQL               │    │
│  │  Campaigns · Segments · Variants · Runs · Metrics · Logs     │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │             CampaignX API Client (httpx)                     │    │
│  │  get_customer_cohort  ·  send_campaign  ·  get_report        │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Brief (text/voice)
    ↓
CampaignBriefAgent → Structured JSON
    ↓
DataFetcher → Real Customer Cohort from API
    ↓
SegmentationAgent → Customer Micro-Segments (with real customer_ids)
    ↓
StrategyAgent → Send Times + A/B Plans (+ Historical Learning)
    ↓
ContentAgent → Email Variants A/B (+ Historical Learning)
    ↓
[Human Approval Gate]
    ↓
ExecutionAgent → Real API Dispatch (send_campaign)
    ↓
AnalyticsAgent → Real Engagement Metrics (get_report)
    ↓
OptimizationAgent → MAB Decisions
    ↓ (loops up to 3 times)
InsightAgent → Actionable Insights
    ↓
Historical Learning Store → Feeds future campaigns
```

---

## 4. Multi-Agent Architecture

CampaignX uses a **sequential pipeline architecture** where each agent is a specialized autonomous unit:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| CampaignBriefAgent | NLP parser | Raw brief text | Structured JSON |
| SegmentationAgent | Customer segmenter | Parsed brief + real cohort data | Micro-segments with customer_ids |
| StrategyAgent | Campaign strategist | Segments + historical learnings | Send times, A/B plans |
| ContentAgent | Copywriter | Brief + strategy + historical learnings | Email variants (A/B per segment) |
| ExecutionAgent | API executor | Approved plan + customer_ids | Real API dispatch results |
| AnalyticsAgent | Metrics collector | Sent campaign IDs | Real open/click rates from API |
| OptimizationAgent | MAB optimizer | Current metrics | Next-loop decisions |
| InsightAgent | Data analyst | All accumulated metrics | Natural language insights |

**Key Design Principles:**
- Each agent has a single responsibility
- All LLM-powered agents inherit from `BaseAgent` which centralizes the Groq LLM client
- Agents communicate through the orchestrator — never directly
- All agent actions are transparently logged with "running" → "completed" states
- Historical learning is injected into StrategyAgent and ContentAgent prompts

### Inheritance Hierarchy

```
                    ┌───────────────┐
                    │   BaseAgent   │
                    │───────────────│
                    │ + client      │  ← Groq (OpenAI SDK)
                    │ + model       │  ← llama-3.1-8b-instant
                    │───────────────│
                    │ _complete_json│  ← Shared JSON completion
                    │ _build_history│  ← Historical context injection
                    └───────┬───────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    Plan Agents        Run Agents      Intelligence
    ────────────       ──────────      ────────────
    BriefAgent         ExecutionAgent  SegmentIntelService
    SegmentAgent       AnalyticsAgent  HistoricalLearningService
    StrategyAgent      OptimizationAgent
    ContentAgent       InsightAgent
```

> Note: `AnalyticsAgent` and `ExecutionAgent` use `CampaignXAPIClient` directly for real API calls rather than LLM function-calling.

---

## 5. Detailed Agent Explanations

### CampaignBriefAgent
- **Purpose**: Accepts a natural language campaign brief (text or voice) and extracts structured fields
- **LLM Role**: NLU parsing
- **Input**: Raw brief string (e.g., *"Run email campaign for XDeposit..."*)
- **Output**: JSON with keys: `product`, `constraints`, `target_segments`, `tone`, `optimization_goal`, `cta_url`
- **Temperature**: 0.2 (deterministic)

### SegmentationAgent
- **Purpose**: Segments real customers from the API cohort into marketing micro-groups
- **LLM Role**: Customer clustering based on real attributes (Occupation, demographics)
- **Input**: Parsed brief + real customer cohort data (from `get_customer_cohort` API)
- **Output**: 2-4 segment dicts with `name`, `customer_count`, `customer_ids` (real IDs)
- **Key Feature**: Builds a statistical summary of the cohort (occupation distribution, sample records) for the LLM prompt

### StrategyAgent
- **Purpose**: Determines optimal send time and A/B testing plan for each segment
- **LLM Role**: Marketing strategy generation
- **Input**: Segments list + optional historical learning context
- **Output**: Strategy per segment: `segment_name`, `send_time`, `variants_count`, `ab_testing_plan`
- **Key Feature**: Historical learnings from past campaigns are injected into the prompt

### ContentAgent
- **Purpose**: Generates two email variants (A and B) per segment
- **LLM Role**: Copywriting with constraint awareness
- **Input**: Parsed brief + strategies + optional historical context
- **Output**: Dict mapping `segment_name` → list of variant dicts (`label`, `subject`, `body`)
- **Rules**: Variant A = professional; Variant B = emojis + concise; constraints apply per-segment

### ExecutionAgent
- **Purpose**: Dispatches campaigns by calling the real `send_campaign` API
- **LLM Role**: None — uses `CampaignXAPIClient` directly
- **Input**: Execution plan (segment_id → variants) + segments with customer_ids
- **Output**: List of dispatch results with `api_campaign_id` for each segment+variant combination
- **Key Feature**: Tracks `api_campaign_id` for later report retrieval

### AnalyticsAgent
- **Purpose**: Fetches real engagement reports from the API
- **LLM Role**: None — uses `CampaignXAPIClient.get_report()` + `compute_rates()`
- **Input**: List of sent campaigns with `api_campaign_id`
- **Output**: Metrics per segment+variant: `open_rate`, `click_rate`, `total_sent`, `total_opened`, `total_clicked`
- **Key Feature**: Computes rates from raw EO (Email Opened) / EC (Email Clicked) flags

### OptimizationAgent
- **Purpose**: Implements Multi-Armed Bandit optimization
- **LLM Role**: MAB analysis and decision-making
- **Input**: Current run metrics
- **Output**: Per-segment decisions: `best_variant`, `action` (exploit/explore ratio), adjustments for send time, subject style, emoji usage; `stop_optimization` flag
- **Stop Condition**: Click rate > 15% on best variant

### InsightAgent
- **Purpose**: Generates human-readable marketing insights from all accumulated metrics
- **LLM Role**: Data-to-narrative transformation
- **Input**: All metrics across optimization loops
- **Output**: List of insights per segment: `segment_name`, `insight_content`

---

## 6. Optimization Loop Explanation

CampaignX runs a **Multi-Armed Bandit (MAB) optimization loop** up to 3 iterations:

```
Loop 1: Execute → Collect Metrics → Analyze → Decide
Loop 2: Apply Adjustments → Execute → Collect → Analyze → Decide  
Loop 3: Final Execution → Collect → Generate Insights
```

**How MAB works in CampaignX:**
1. **Exploration**: In early loops, both variants (A and B) are tested equally
2. **Exploitation**: In later loops, the winning variant gets prioritized (~70% exploit, ~30% explore)
3. **Stop Condition**: If click rate exceeds 15%, optimization stops early
4. **Adjustments**: Each loop can modify send time, subject style, and emoji usage based on performance data
5. **Convergence**: The system typically needs 2-3 loops to identify the winning variant

---

## 7. Dynamic API Discovery

The system includes an **OpenAPI specification discovery** layer:

1. `openapi_loader.py` loads and parses `openapi.json`
2. Extracts available endpoints, schemas, and parameters
3. Converts them into OpenAI-compatible function-calling tool format
4. `dynamic_tool_registry.py` registers callable HTTP handlers for each endpoint

This infrastructure allows the system to **adapt to new APIs without code changes** — just update the OpenAPI spec file.

> Note: In the current implementation, `ExecutionAgent` and `AnalyticsAgent` use the dedicated `CampaignXAPIClient` for direct API calls. The dynamic discovery layer provides the foundation for future zero-code API integrations.

---

## 8. Intelligence Features

CampaignX features five intelligence layers that transform the platform from a campaign executor into a **learning marketing intelligence system**:

| Feature | Location | Purpose |
|---------|----------|---------|
| Segment Intelligence | Approval Page (expandable rows) | AI explanations for each customer segment |
| Historical Learning | Campaign Brief Page | Accumulated knowledge from past campaigns |
| Optimization Timeline | Dashboard | Line chart showing improvement across loops |
| Campaign Lifecycle | Dashboard (left panel) | 9-stage vertical timeline with status |
| Live Agent Feed | Dashboard + Approval Page | Real-time agent activity with animations |

---

## 9. Segment Intelligence

**Location**: Approval Page → Segment Table (expandable rows)

Each customer segment gets an AI-generated intelligence summary that explains:
- What makes the segment unique
- Their engagement patterns and preferences
- The best marketing approach for them

**Example Output:**
> **Female Senior Citizens** — High engagement during morning hours and respond better to friendly, professional tone. Extra 0.25% return incentive drives strong CTA click-through.

**Technical Implementation:**
- `SegmentIntelligenceService` (inherits `BaseAgent`) aggregates segment demographics and performance metrics
- Uses Groq LLM (llama-3.1-8b-instant) to generate concise 2-3 sentence explanations
- Includes fallback intelligence when LLM is unavailable
- API: `GET /campaigns/{id}/segment-intelligence`

---

## 10. Historical Campaign Learning

**Location**: Campaign Brief Page (below the input form)

The platform **learns from past campaigns** and surfaces accumulated knowledge:

**Example Learnings:**
> 🧪 *Emoji subject lines increased open rate by 8% for customers aged 18–35.* (high confidence)

> 🧪 *Morning campaigns produced 12% higher engagement among senior customers.* (medium confidence)

**How It Works:**
1. After each campaign completes, the InsightAgent generates per-segment insights
2. These insights are stored in the `campaign_insights` table
3. `HistoricalLearningService` queries all past insights
4. Groq LLM extracts recurring patterns and assigns confidence levels
5. Learnings are displayed on the campaign creation page

**Learning Injection:**
Historical context is also **injected into StrategyAgent and ContentAgent prompts**, so future campaigns are directly influenced by past performance:

```
Historical Campaign Learning:
- [young_professionals] Variant B with emoji outperformed by 3.2%
- [female_senior_citizens] Morning send times drove 12% higher open rates

Use these insights to inform your strategy and content generation.
```

---

## 11. Optimization Timeline Visualization

**Location**: Dashboard Page

A Recharts **line chart** visualizing campaign improvement across optimization runs:

| Run | Open Rate | Click Rate | Best Variant |
|-----|-----------|------------|--------------|
| 1   | 16.2%     | 5.8%       | Variant A    |
| 2   | 18.5%     | 8.2%       | Variant B    |
| 3   | 19.1%     | 11.4%      | Variant B    |

The chart shows two lines (open rate in purple, click rate in green) progressing across runs, with summary cards below.

**API:** `GET /campaigns/{id}/optimization-timeline`

---

## 12. Campaign Lifecycle Timeline

**Location**: Dashboard Page (left column)

A **vertical timeline** showing all 9 stages of the campaign lifecycle:

1. ✔ Campaign Created
2. ✔ Strategy Generated
3. ✔ Segments Created
4. ✔ Email Variants Generated
5. ✔ Human Approval
6. ⏳ Campaign Executed
7. ○ Metrics Collected
8. ○ Optimization Completed
9. ○ Insights Generated

Updates **dynamically** as each stage completes, using agent log data and campaign status. Status icons: ✔ completed, ⏳ running, ○ pending.

---

## 13. Live Agent Activity Feed

**Location**: Dashboard Page (right column) and Approval Page

A real-time terminal-style panel showing agents working step-by-step:

```
⏳ [CampaignBriefAgent] Parsing campaign brief
✔ [CampaignBriefAgent] Parsed campaign brief into structured data
⏳ [DataFetcher] Fetching real customer cohort data
✔ [DataFetcher] Retrieved 150 customers from API
⏳ [SegmentationAgent] Creating micro-segments from real customer cohort
✔ [SegmentationAgent] Created customer micro-segments from real cohort data
⏳ [StrategyAgent] Selecting optimal send times and A/B test plans
✔ [StrategyAgent] Generated segment strategies with historical learning
```

**Features:**
- Progressive log entries that appear as agents work
- Status icons: ✔ completed, ⏳ running, ⚠ error
- CSS fade-in animation for new entries
- Auto-scroll to latest entry
- "● Live" indicator when agents are actively running
- 3-second polling interval

---

## 14. Tech Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Backend** | FastAPI (Python) | Latest | Async REST API server |
| **AI/LLM** | Groq (llama-3.1-8b-instant) | Free tier | Agent reasoning (JSON mode) via OpenAI-compatible SDK |
| **Database** | SQLite + SQLAlchemy ORM | 2.x | Persistent storage (7 models) |
| **HTTP Client** | HTTPX | Latest | Async external API calls |
| **Config** | Pydantic Settings | 2.x | Type-safe env configuration |
| **Frontend** | React + Vite | 19 + 7 | Single-page application |
| **Styling** | Tailwind CSS | 4.x | Utility-first CSS framework |
| **Charts** | Recharts | 3.x | Line + Bar chart data viz |
| **Icons** | Lucide React | Latest | Clean SVG icon library |
| **HTTP Client** | Axios | 1.x | Frontend API communication |
| **Voice Input** | Web Speech API | Native | Browser speech-to-text |
| **Server** | Uvicorn | Latest | ASGI production server |

---

## 15. Database Schema

CampaignX uses **7 ORM models** managed by SQLAlchemy:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Campaign   │1───*│   Segment    │1───*│ EmailVariant │
│──────────────│     │──────────────│     │──────────────│
│ id (PK)      │     │ id (PK)      │     │ id (PK)      │
│ brief        │     │ campaign_id  │     │ segment_id   │
│ product      │     │ name         │     │ variant_label│
│ constraints  │     │ customer_cnt │     │ subject      │
│ target_segs  │     │ customer_ids │     │ body         │
│ tone         │     └──────────────┘     └──────────────┘
│ opt_goal     │
│ cta_url      │
│ status       │     ┌──────────────┐     ┌──────────────────┐
│ created_at   │1───*│ CampaignRun  │1───*│PerformanceMetric │
└──────┬───────┘     │──────────────│     │──────────────────│
       │             │ campaign_id  │     │ run_id           │
       │             │ loop_index   │     │ segment_id       │
       │             │ status       │     │ variant_id       │
       │             │ api_camp_id  │     │ open_rate        │
       │             │ executed_time│     │ click_rate       │
       │             └──────────────┘     └──────────────────┘
       │
       ├──1──*─┌──────────────┐
       │       │  AgentLog    │
       │       │──────────────│
       │       │ agent_name   │
       │       │ status       │  ← running / completed / error
       │       │ action_desc  │
       │       │ input_data   │  ← JSON string
       │       │ output_data  │  ← JSON string
       │       │ reasoning    │
       │       │ timestamp    │
       │       └──────────────┘
       │
       └──1──*─┌────────────────┐
               │CampaignInsight │
               │────────────────│
               │ segment_name   │
               │ insight_content│
               │ timestamp      │
               └────────────────┘
```

**Campaign Status Flow:** `draft` → `generating` → `pending_approval` → `approved` → `running` → `completed`

---

## 16. API Reference

All endpoints are prefixed with `/campaigns` unless noted.

### Health Check

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns `{"status": "ok"}` |

### Campaign Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/campaigns/start` | Create campaign from brief, starts async agent pipeline |
| GET | `/campaigns/` | List all campaigns |
| GET | `/campaigns/{id}` | Get single campaign with segments and variants |
| POST | `/campaigns/{id}/approve` | Approve campaign, starts execution + optimization loop |
| POST | `/campaigns/{id}/reject` | Reject campaign, resets to draft |

### Metrics & Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/campaigns/{id}/metrics` | Get all optimization runs with metrics |
| GET | `/campaigns/{id}/optimization-timeline` | Get averaged metrics per run for timeline chart |

### Intelligence

| Method | Path | Description |
|--------|------|-------------|
| GET | `/campaigns/{id}/insights` | Get AI-generated marketing insights |
| GET | `/campaigns/{id}/segment-intelligence` | Get AI explanations for each segment |
| GET | `/campaigns/learning` | Get accumulated learnings from all past campaigns |

### Agent Logs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/campaigns/{id}/logs` | Get agent logs for a specific campaign |
| GET | `/campaigns/logs` | Get all agent logs across all campaigns |

### Request/Response Examples

**Start Campaign:**
```bash
POST /campaigns/start
Content-Type: application/json

{
  "brief": "Run email campaign for XDeposit offering 1% higher returns. Give 0.25% extra for female senior citizens. Optimize for CTR and Open Rate."
}
```

**Response:**
```json
{
  "id": 1,
  "brief": "Run email campaign for XDeposit...",
  "status": "generating",
  "segments": [],
  "created_at": "2026-03-06T10:00:00"
}
```

---

## 17. Project Structure

```
campaignx/
├── .env.example                         # Sample environment configuration
├── openapi.json                         # CampaignX API OpenAPI specification
├── README.md                            # This file
│
├── backend/
│   ├── main.py                          # FastAPI app entry point (CORS, health)
│   ├── config.py                        # Pydantic Settings (reads .env)
│   ├── database.py                      # SQLAlchemy engine & session factory
│   ├── models.py                        # 7 ORM models
│   ├── schemas.py                       # Pydantic request/response schemas
│   ├── requirements.txt                 # Python dependencies
│   │
│   ├── agents/                          # AI Agent implementations
│   │   ├── base_agent.py                # Shared Groq LLM client + JSON completion
│   │   ├── campaign_brief_agent.py      # NLP brief parser
│   │   ├── segmentation_agent.py        # Customer micro-segmentation
│   │   ├── strategy_agent.py            # Send time & A/B strategy (+ history)
│   │   ├── content_agent.py             # Email variant generator (+ history)
│   │   ├── execution_agent.py           # Real API campaign dispatcher
│   │   ├── analytics_agent.py           # Real report metric collector
│   │   ├── optimization_agent.py        # Multi-armed bandit optimizer
│   │   └── insight_agent.py             # Natural language insight generator
│   │
│   ├── api/
│   │   └── campaign_api.py              # All REST endpoints
│   │
│   ├── orchestrator/
│   │   └── agent_orchestrator.py        # Pipeline engine with _run_agent() helper
│   │
│   ├── services/
│   │   ├── campaign_service.py          # Campaign CRUD + brief/segment/variant persistence
│   │   ├── analytics_service.py         # Run creation & metric persistence
│   │   ├── optimization_service.py      # Optimization state management
│   │   ├── insight_service.py           # Insight storage & retrieval
│   │   ├── segment_intelligence_service.py  # AI segment explanations
│   │   └── historical_learning_service.py   # Cross-campaign learning
│   │
│   ├── custom_logging/
│   │   └── agent_logger.py              # Progressive agent action logging
│   │
│   └── tools/
│       ├── openapi.json                 # OpenAPI specification (dynamic API discovery)
│       ├── openapi_loader.py            # Spec parser → function tool schemas
│       ├── dynamic_tool_registry.py     # Runtime tool execution via HTTP
│       └── campaignx_api_client.py      # Centralized async API client
│
├── frontend/
│   ├── package.json                     # Node dependencies
│   ├── vite.config.js                   # Vite build configuration
│   ├── index.html                       # HTML entry point
│   └── src/
│       ├── main.jsx                     # React entry point (BrowserRouter)
│       ├── App.jsx                      # Router & navigation bar
│       ├── index.css                    # Global styles (Tailwind)
│       ├── App.css                      # App-level styles
│       │
│       ├── api/
│       │   └── backendClient.js         # Axios instance (base URL config)
│       │
│       ├── components/
│       │   ├── AgentLogsPanel.jsx        # Live terminal-style agent feed
│       │   ├── SegmentTable.jsx          # Segment table + intelligence rows
│       │   ├── MetricsChart.jsx          # Bar chart for per-run metrics
│       │   ├── EmailVariantCard.jsx      # Email preview card
│       │   ├── OptimizationTimelineChart.jsx  # Line chart across runs
│       │   ├── CampaignTimeline.jsx      # 9-stage lifecycle timeline
│       │   └── HistoricalLearningPanel.jsx    # Past campaign learnings
│       │
│       └── pages/
│           ├── CampaignBriefPage.jsx     # Campaign creation + voice + learnings
│           ├── ApprovalPage.jsx          # Human review + segment intelligence
│           ├── DashboardPage.jsx         # Analytics dashboard + timeline + chart
│           └── AgentLogsPage.jsx         # Global agent reasoning trace
│
└── docs/
    ├── architecture.md                  # System architecture documentation
    ├── tech_stack.md                    # Complete tech stack reference
    └── workflow.md                      # Campaign workflow & pipeline docs
```

---

## 18. Setup Instructions

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **Groq API key** (free at [console.groq.com](https://console.groq.com) — for AI agent reasoning)
- **CampaignX API key** (for real campaign execution — optional for demo)

### Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/campaignx.git
cd campaignx

# 2. Create Python virtual environment
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment
cp ../.env.example .env
# Edit .env and add your GROQ_API_KEY (required, free at console.groq.com)
# Also add CAMPAIGNX_API_KEY and CAMPAIGNX_BASE_URL (required for API calls)

# 5. Start the backend server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
# In a new terminal
cd frontend

# 1. Install Node dependencies
npm install

# 2. Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173` and the backend API at `http://localhost:8000`.

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI).

---

## 19. Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GROQ_API_KEY` | ✅ Yes | `""` | Powers all 8 AI agents and intelligence services (free at console.groq.com) |
| `DATABASE_URL` | ❌ No | `sqlite:///./campaignx.db` | Database connection string |
| `CAMPAIGNX_API_KEY` | ✅ Yes | `""` | CampaignX external API authentication (required for campaign execution) |
| `CAMPAIGNX_BASE_URL` | ❌ No | `https://campaignx.inxiteout.ai` | CampaignX external API base URL |

**.env file example:**
```bash
GROQ_API_KEY=gsk-your-groq-api-key
DATABASE_URL=sqlite:///./campaignx.db
CAMPAIGNX_API_KEY=your-campaignx-key
CAMPAIGNX_BASE_URL=https://campaignx.inxiteout.ai
```

---

## 20. Demo Walkthrough

### Step 1: Create a Campaign
Navigate to the home page. You'll see the **Historical Campaign Learnings** panel (populated after your first campaign). Type or speak a campaign brief:

> *"Run an email campaign for XDeposit offering 1% higher returns. Give 0.25% extra for female senior citizens. Optimize for CTR and open rate."*

Click **Generate Campaign Plan**.

### Step 2: Watch Agents Work
You're redirected to the **Approval Page**. Watch the **Live Agent Activity Feed** as agents work:
- CampaignBriefAgent parses the brief
- DataFetcher retrieves real customer cohort from the API
- SegmentationAgent creates micro-segments from real customer data
- StrategyAgent determines send times (using historical learning)
- ContentAgent generates A/B email variants (using historical learning)

### Step 3: Review & Approve
Once agents complete, review:
- **Segment Table**: Click any segment row to expand **Segment Intelligence** explanations
- **Email Variants**: Review A/B variants for each segment
- Click **Approve & Execute**

### Step 4: Monitor Optimization
On the **Dashboard**, watch:
- **Campaign Lifecycle Timeline**: Stages light up as they complete
- **Agent Activity Feed**: Shows execution, analytics, and optimization agents working
- **Optimization Timeline Chart**: Line chart shows click/open rates improving across loops
- **Per-Run Metrics**: Bar charts for each optimization loop
- **AI Marketing Insights**: Natural language insights after completion

### Step 5: Learn
Return to the home page. The **Historical Campaign Learnings** panel now shows patterns extracted from your completed campaign, ready to influence the next one.

---

## 21. Example Campaign Scenario

**Brief Input:**
> "Launch email campaign for XDeposit fixed deposit product targeting senior citizens and young professionals. Female senior citizens get extra 0.25% returns. Use professional tone. Optimize for open rate and click rate."

**Agent Pipeline Result:**

| Stage | Output |
|-------|--------|
| Brief Parsed | Product: XDeposit, Tone: professional, Segments: [senior_citizens, young_professionals, female_senior_citizens] |
| Cohort Fetched | 150 real customers from `get_customer_cohort` API |
| Segments Created | 3-4 micro-segments with real customer_ids assigned |
| Strategy Generated | Morning sends for seniors, evenings for professionals; emoji vs professional subject A/B test |
| Variants Generated | 6-8 email variants (2 per segment: A=professional, B=emoji/concise) |
| Execution | Campaign dispatched via `send_campaign` API to real customers |
| Analytics | Real open/click metrics fetched via `get_report` API |
| Optimization | 3 loops: click rate improved from ~5% → ~8% → ~11% |
| Insights | "Variant B outperforms for young professionals," "Morning sends +12% for seniors" |

---

## 22. Example AI Insights Output

After a campaign completes, the InsightAgent generates insights like:

```json
[
  {
    "segment_name": "female_senior_citizens",
    "insight_content": "Variant B with emoji subject line achieved 14.2% click rate, 
     outperforming Variant A (10.8%) by 3.4 percentage points. 
     Morning send time (9:00 AM) consistently produced higher open rates. 
     The extra 0.25% return incentive in the body text drove strong CTA engagement."
  },
  {
    "segment_name": "young_professionals",
    "insight_content": "Shorter subject lines with emoji (Variant B) drove 12.1% click rate 
     vs 8.7% for professional Variant A. Evening send times (7:00 PM) showed 
     15% higher engagement. Concise body format outperformed detailed content."
  }
]
```

**Historical Learnings extracted:**
- 🧪 *Emoji subject lines increase open rate by 8% for customers aged 18-35* (high confidence)
- 🧪 *Morning campaigns produce 12% higher engagement among senior customers* (high confidence)
- 🧪 *Concise email bodies outperform detailed ones for young professional segments* (medium confidence)

---

## 23. Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Multi-Agent Architecture** | Each agent has a single responsibility, making the system modular, testable, and extensible |
| **Multi-Armed Bandit over A/B** | MAB dynamically balances exploration/exploitation, converging faster with less wasted traffic |
| **Real API Integration** | `CampaignXAPIClient` handles all external calls (`send_campaign`, `get_report`, `get_customer_cohort`) |
| **Dynamic API Discovery** | `OpenAPILoader` + `DynamicToolRegistry` enable zero-code integration with any OpenAPI service |
| **Historical Learning Injection** | Learnings are injected directly into agent prompts, creating a genuine feedback loop |
| **Progressive Agent Logs** | "running" → "completed" status creates a live feed for AI reasoning transparency |
| **BaseAgent Inheritance** | Centralizes Groq LLM init + JSON completion — DRY, single point of change |
| **SQLite (dev)** | Zero-config persistence; trivially swapped to PostgreSQL via `DATABASE_URL` |
| **Background Tasks** | FastAPI background tasks keep API responsive during long agent orchestration |

---

## 24. Troubleshooting

### Backend won't start

- **`GROQ_API_KEY` not set**: Ensure `.env` file exists in `backend/` directory with a valid Groq key (free at [console.groq.com](https://console.groq.com))
- **Port 8000 in use**: Change port with `uvicorn main:app --port 8001`
- **Module not found**: Ensure virtual environment is activated (`source venv/bin/activate`)

### Frontend won't start

- **Dependencies not installed**: Run `npm install` in the `frontend/` directory
- **Port 5173 in use**: Vite will auto-increment to 5174

### Campaign generation hangs

- Verify the Groq API key is valid (free tier has generous limits)
- Check the backend terminal for error logs from agents
- The campaign status should transition: `generating` → `pending_approval`

### No metrics after approval

- The `CAMPAIGNX_API_KEY` must be set for campaign execution (sign up at the CampaignX API)
- The `send_time` format must be `DD:MM:YY HH:MM:SS` (IST) — e.g., `15:03:26 10:00:00`
- A 422 error from the API usually means incorrect `send_time` format or invalid customer IDs
- Without a valid API key, `send_campaign` calls will fail silently
- Check backend logs for "Failed to send campaign" errors

### Agent logs not appearing

- Verify the frontend is polling the correct endpoint (`/campaigns/{id}/logs`)
- Check that the campaign ID exists in the database
- Agent logs appear progressively — wait a few seconds during generation

### Database reset

If you need a fresh start:
```bash
cd backend
rm campaignx.db        # Delete the SQLite database
# Restart the server — tables will be auto-created
```

---

## 25. Future Improvements

- **WebSocket Real-Time Updates**: Replace polling with WebSocket connections for truly real-time agent activity feeds
- **Production Database**: Migrate from SQLite to PostgreSQL for concurrent access and production workloads
- **Real Email Integration**: Connect ExecutionAgent to SendGrid, Mailchimp, or AWS SES for actual email dispatch
- **Advanced MAB Algorithms**: Implement Thompson Sampling or UCB algorithms for faster convergence
- **Multi-Channel Campaigns**: Extend beyond email to SMS, push notifications, and social media
- **User Authentication**: Add JWT-based auth for multi-user access
- **Campaign Templates**: Pre-built campaign templates for common scenarios
- **A/B Testing Dashboard**: Detailed statistical significance testing for variant comparisons
- **Custom Segment Builder**: Allow users to define their own segmentation criteria
- **Webhook Integration**: Real-time metric ingestion from external analytics platforms
- **Agent Memory**: Long-term memory for agents to remember preferences across campaigns

---

<p align="center">
  <strong>Built with ❤️ for hackathon excellence</strong><br/>
  <em>CampaignX — Where AI meets marketing intelligence</em>
</p>
