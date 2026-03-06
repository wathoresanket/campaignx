# CampaignX — System Architecture

## High-Level Overview

CampaignX is a **multi-agent AI marketing intelligence platform** that uses autonomous AI agents to plan, execute, and optimize email campaigns — with a human-in-the-loop approval gate.

```
┌────────────────────────────────────────────────────────────────────────┐
│                         CampaignX Platform                            │
│                                                                       │
│  ┌─────────────┐    ┌──────────────────┐    ┌─────────────────────┐  │
│  │   React UI  │◄──►│  FastAPI Backend  │◄──►│  SQLite Database    │  │
│  │  (Vite SPA) │    │  (REST API)       │    │  (auto-created)     │  │
│  └─────────────┘    └────────┬─────────┘    └─────────────────────┘  │
│                              │                                        │
│                    ┌─────────▼──────────┐                            │
│                    │  Agent Orchestrator │                            │
│                    │  (Pipeline Engine)  │                            │
│                    └─────────┬──────────┘                            │
│                              │                                        │
│         ┌────────────────────┼────────────────────┐                  │
│         ▼                    ▼                    ▼                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐          │
│  │  AI Agents   │  │  Services    │  │  External Tools   │          │
│  │  (8 agents)  │  │  (6 services)│  │  (CampaignX API)  │          │
│  └──────────────┘  └──────────────┘  └──────────────────┘          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Three-Tier Architecture

### 1. Presentation Layer — React SPA
- **4 pages**: Campaign Brief → Approval → Dashboard → Agent Logs
- **Real-time polling**: Auto-refreshes every 3-5 seconds during execution
- **Recharts visualizations**: Optimization timeline (line), metrics (bar)
- **Voice input**: Web Speech API for hands-free brief entry
- **Intelligence panels**: Segment Intelligence, Historical Learnings

### 2. Application Layer — FastAPI + Agent Orchestrator
- **RESTful API**: 12 endpoints with Pydantic schema validation
- **Background task execution**: Non-blocking campaign orchestration
- **BaseAgent pattern**: All 8 AI agents inherit shared LLM infrastructure
- **Progressive logging**: "running" → "completed" status for every agent action
- **Centralized API client**: `CampaignXAPIClient` handles all external API calls

### 3. Data Layer — SQLAlchemy + SQLite
- **7 ORM models**: Campaign, Segment, EmailVariant, CampaignRun, PerformanceMetric, AgentLog, CampaignInsight
- **Zero-config**: Auto-creates database on first run
- **Production-ready**: Swappable to PostgreSQL via `DATABASE_URL`

---

## Agent Architecture (Inheritance Pattern)

```
                    ┌───────────────┐
                    │   BaseAgent   │
                    │───────────────│
                    │ + client      │  ← AsyncOpenAI singleton
                    │ + model       │  ← gpt-4o-mini
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

> Note: `ExecutionAgent` and `AnalyticsAgent` use `CampaignXAPIClient` directly for real API calls (send_campaign, get_report).

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Sequential agent pipeline** | Each agent's output feeds the next; ensures deterministic flow |
| **Human-in-the-loop gate** | Between planning and execution — prevents auto-sending unreviewed content |
| **BaseAgent inheritance** | Centralizes OpenAI init — DRY principle, single point of change |
| **Background task execution** | Non-blocking API — frontend stays responsive during long AI calls |
| **CampaignXAPIClient** | Centralized async client for all external API interactions (cohort, send, report) |
| **Dynamic API discovery** | OpenAPI spec parser + tool registry for future zero-code API integrations |
| **Historical learning injection** | Past insights injected into agent prompts for continuous improvement |
| **SQLite default** | Zero-config for hackathon demo; one env var swap to production DB |
