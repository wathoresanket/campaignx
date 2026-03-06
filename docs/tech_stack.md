# CampaignX — Tech Stack

## Stack Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                          FRONTEND                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  React   │  │   Vite   │  │ Tailwind │  │ Recharts │            │
│  │  19.x    │  │   7.x    │  │ CSS 4.x  │  │  3.x     │            │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘            │
│  ┌──────────┐  ┌────────────┐  ┌────────────────────────┐          │
│  │  Axios   │  │ React      │  │ Web Speech API         │          │
│  │          │  │ Router DOM │  │ (voice input)           │          │
│  └──────────┘  └────────────┘  └────────────────────────┘          │
├──────────────────────────────────────────────────────────────────────┤
│                          BACKEND                                      │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐              │
│  │  Python  │  │  FastAPI     │  │  SQLAlchemy      │              │
│  │  3.10+   │  │  (async)     │  │  (ORM)           │              │
│  └──────────┘  └──────────────┘  └──────────────────┘              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────────┐              │
│  │  Pydantic│  │  OpenAI SDK  │  │  HTTPX           │              │
│  │  (schema)│  │  (async)     │  │  (HTTP client)   │              │
│  └──────────┘  └──────────────┘  └──────────────────┘              │
├──────────────────────────────────────────────────────────────────────┤
│                         DATABASE                                      │
│  ┌────────────────────────────────────────────┐                      │
│  │  SQLite (dev) / PostgreSQL (production)    │                      │
│  │  Auto-created via SQLAlchemy metadata      │                      │
│  └────────────────────────────────────────────┘                      │
├──────────────────────────────────────────────────────────────────────┤
│                        AI / ML LAYER                                  │
│  ┌──────────────┐  ┌──────────────────────────────────┐              │
│  │  GPT-4o-mini │  │  Multi-Armed Bandit (MAB)        │              │
│  │  (all agents)│  │  (optimization algorithm)        │              │
│  └──────────────┘  └──────────────────────────────────┘              │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Frontend Stack (Detailed)

| Technology | Version | Purpose | Why Chosen |
|-----------|---------|---------|------------|
| **React** | 19.x | UI framework | Component-based, rich ecosystem, industry standard |
| **Vite** | 7.x | Build tool & dev server | Lightning-fast HMR, minimal config, ESBuild-powered |
| **Tailwind CSS** | 4.x | Utility-first styling | Rapid UI development, consistent design system |
| **Recharts** | 3.x | Data visualization | React-native charting, built on D3, declarative API |
| **React Router** | 7.x | Client-side routing | SPA navigation between 4 pages |
| **Axios** | 1.x | HTTP client | Promise-based, interceptors, cleaner than fetch |
| **Lucide React** | Latest | Icon library | Clean SVG icons, tree-shakeable |
| **Web Speech API** | Native | Voice input | Browser-native, no dependency needed |

### Frontend Architecture
```
src/
├── api/
│   └── backendClient.js         ← Axios instance (base URL config)
├── components/
│   ├── AgentLogsPanel.jsx       ← Live agent activity feed
│   ├── CampaignTimeline.jsx     ← 9-stage lifecycle visualization
│   ├── EmailVariantCard.jsx     ← A/B variant preview
│   ├── HistoricalLearningPanel.jsx ← Past campaign knowledge
│   ├── MetricsChart.jsx         ← Bar chart for run metrics
│   ├── OptimizationTimelineChart.jsx ← Line chart across runs
│   └── SegmentTable.jsx         ← Segments with AI intelligence
└── pages/
    ├── CampaignBriefPage.jsx    ← Input + voice + historical learnings
    ├── ApprovalPage.jsx         ← Review & approve/reject
    ├── DashboardPage.jsx        ← Analytics + timeline + insights
    └── AgentLogsPage.jsx        ← Full agent reasoning trace
```

---

## Backend Stack (Detailed)

| Technology | Version | Purpose | Why Chosen |
|-----------|---------|---------|------------|
| **Python** | 3.10+ | Language | Async support, rich AI/ML ecosystem |
| **FastAPI** | Latest | Web framework | Async-first, auto-docs, Pydantic integration |
| **SQLAlchemy** | 2.x | ORM | Mature, database-agnostic, relationship mapping |
| **Pydantic** | 2.x | Schema validation | Type-safe request/response models, auto-serialization |
| **OpenAI SDK** | 1.x (async) | LLM integration | Official Python client, async support |
| **HTTPX** | Latest | HTTP client | Async HTTP for external API calls |
| **Uvicorn** | Latest | ASGI server | Production-grade, async event loop |

### Backend Architecture
```
backend/
├── main.py                      ← FastAPI app entry point
├── config.py                    ← Pydantic Settings (reads .env)
├── database.py                  ← SQLAlchemy session factory
├── models.py                    ← 7 ORM models
├── schemas.py                   ← Pydantic request/response schemas
├── agents/
│   ├── base_agent.py            ← Shared OpenAI client + JSON completion
│   ├── campaign_brief_agent.py
│   ├── segmentation_agent.py
│   ├── strategy_agent.py
│   ├── content_agent.py
│   ├── execution_agent.py
│   ├── analytics_agent.py
│   ├── optimization_agent.py
│   └── insight_agent.py
├── orchestrator/
│   └── agent_orchestrator.py    ← Pipeline engine with _run_agent() helper
├── services/
│   ├── campaign_service.py
│   ├── analytics_service.py
│   ├── optimization_service.py
│   ├── insight_service.py
│   ├── segment_intelligence_service.py
│   └── historical_learning_service.py
├── tools/
│   ├── openapi.json             ← CampaignX API specification
│   ├── openapi_loader.py        ← Spec parser
│   ├── dynamic_tool_registry.py ← Runtime tool execution
│   └── campaignx_api_client.py  ← Centralized async API client
└── custom_logging/
    └── agent_logger.py          ← Progressive agent logging
```

---

## AI / ML Layer

### GPT-4o-mini (OpenAI)
- **Used by**: All 8 AI agents + 2 intelligence services
- **Mode**: Structured JSON output (`response_format: json_object`)
- **Temperature**: 0.2–0.3 (deterministic, low creativity for reliability)
- **Pattern**: BaseAgent → `_complete_json()` shared across all agents

### Multi-Armed Bandit (MAB) Algorithm
- **Purpose**: Continuous A/B testing optimization
- **Strategy**: Epsilon-greedy (70% exploit / 30% explore)
- **Decision variables**: Send time, subject style, emoji usage
- **Convergence**: Stops when best variant achieves >15% click rate

---

## Database Schema

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Campaign   │◄───►│   Segment    │◄───►│ EmailVariant │
│──────────────│     │──────────────│     │──────────────│
│ id           │     │ id           │     │ id           │
│ brief        │     │ campaign_id  │     │ segment_id   │
│ product      │     │ name         │     │ variant_label│
│ tone         │     │ customer_cnt │     │ subject      │
│ status       │     │ customer_ids │     │ body         │
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ├──►┌──────────────┐     ┌──────────────────┐
       │   │ CampaignRun  │◄───►│PerformanceMetric │
       │   │──────────────│     │──────────────────│
       │   │ campaign_id  │     │ run_id           │
       │   │ loop_index   │     │ segment_id       │
       │   │ status       │     │ variant_id       │
       │   └──────────────┘     │ open_rate        │
       │                        │ click_rate       │
       │                        └──────────────────┘
       │
       ├──►┌──────────────┐
       │   │  AgentLog    │
       │   │──────────────│
       │   │ agent_name   │
       │   │ status       │  ← running / completed / error
       │   │ action_desc  │
       │   │ reasoning    │
       │   └──────────────┘
       │
       └──►┌────────────────┐
           │CampaignInsight │
           │────────────────│
           │ segment_name   │
           │ insight_content│
           └────────────────┘
```

---

## Environment & Configuration

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | ✅ Yes | `""` | Powers all 8 AI agents |
| `DATABASE_URL` | ❌ No | `sqlite:///./campaignx.db` | Database connection |
| `CAMPAIGNX_API_KEY` | ❌ No | `""` | External API authentication |
| `CAMPAIGNX_BASE_URL` | ❌ No | `https://campaignx.superb.ai` | External API base URL |

### Quick Start
```bash
# Backend
cd backend && pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```
