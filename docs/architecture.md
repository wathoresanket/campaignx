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
│  │  (8 agents)  │  │  (6 services)│  │  (OpenAPI-based)  │          │
│  └──────────────┘  └──────────────┘  └──────────────────┘          │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Three-Tier Architecture

### 1. Presentation Layer — React SPA
- **4 pages**: Campaign Brief → Approval → Dashboard → Agent Logs
- **Real-time polling**: Auto-refreshes every 5 seconds during execution
- **Recharts visualizations**: Optimization timeline, metrics charts
- **Voice input**: Web Speech API for hands-free brief entry

### 2. Application Layer — FastAPI + Agent Orchestrator
- **RESTful API**: 10+ endpoints with Pydantic schema validation
- **Background task execution**: Non-blocking campaign orchestration
- **BaseAgent pattern**: All 8 AI agents inherit shared LLM infrastructure
- **Progressive logging**: "running" → "completed" status for every agent action

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
                    │ - client      │  ← AsyncOpenAI singleton
                    │ - model       │  ← gpt-4o-mini
                    │───────────────│
                    │ _complete_json│  ← Shared JSON completion
                    │ _build_history│  ← Historical context injection
                    └───────┬───────┘
                            │
         ┌──────────────────┼──────────────────┐
         │                  │                  │
    Plan Agents        Run Agents      Intelligence
    ────────────       ──────────      ────────────
    BriefAgent         ExecutionAgent  SegmentIntel
    SegmentAgent       AnalyticsAgent  HistoricalLearning
    StrategyAgent      OptimizationAgent
    ContentAgent       InsightAgent
```

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Sequential agent pipeline** | Each agent's output feeds the next; ensures deterministic flow |
| **Human-in-the-loop gate** | Between planning and execution — prevents auto-sending bad content |
| **BaseAgent inheritance** | Centralizes OpenAI init — DRY principle, single point of change |
| **Background task execution** | Non-blocking API — frontend stays responsive during long AI calls |
| **Dynamic API discovery** | ExecutionAgent reads OpenAPI specs — zero-code integration with external services |
| **SQLite default** | Zero-config for hackathon demo; one env var swap to production DB |
