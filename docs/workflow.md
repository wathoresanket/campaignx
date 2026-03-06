# CampaignX — Workflow & Pipeline

## End-to-End Campaign Workflow

The platform follows a **two-phase pipeline** with a human approval gate in between.

```
 PHASE 1 — PLAN                    GATE              PHASE 2 — RUN
┌─────────────────────┐     ┌──────────────┐    ┌──────────────────────┐
│ Brief → Segmentation│     │  Human       │    │ Execution → Analytics│
│ → Strategy → Content│────►│  Approval    │───►│ → MAB Optimization   │
│                     │     │  (review UI) │    │ → Insights           │
└─────────────────────┘     └──────────────┘    └──────────────────────┘
     ~30 seconds                manual              3 loops × ~20 sec
```

---

## Phase 1: Campaign Planning (Automated)

```
Step 1                Step 2                 Step 3                Step 4
┌──────────┐    ┌────────────────┐    ┌──────────────┐    ┌──────────────┐
│ Campaign │    │  Segmentation  │    │   Strategy   │    │   Content    │
│  Brief   │───►│    Agent       │───►│    Agent     │───►│    Agent     │
│  Agent   │    │                │    │              │    │              │
└──────────┘    └────────────────┘    └──────────────┘    └──────────────┘
     │                 │                    │                    │
     ▼                 ▼                    ▼                    ▼
 Structured       2-4 Micro-          Send Times,         A/B Email
 JSON Brief       Segments            A/B Plans           Variants
```

| Agent | Input | Output | LLM Role |
|-------|-------|--------|----------|
| **CampaignBriefAgent** | Natural language brief | Structured JSON (product, tone, segments, constraints) | NLU parsing |
| **SegmentationAgent** | Parsed brief + cohort data | 2-4 micro-segments with customer counts | Customer clustering |
| **StrategyAgent** | Segments + historical learnings | Send times + A/B testing plans per segment | Marketing strategy |
| **ContentAgent** | Brief + strategies + historical learnings | 2 email variants (A/B) per segment | Copywriting |

### Historical Learning Injection
- Past campaign insights are automatically queried from the database
- Injected into **StrategyAgent** and **ContentAgent** prompts
- Creates a continuous learning loop: each campaign improves the next

---

## Human Approval Gate

```
┌─────────────────────────────────────────────────┐
│              Approval Page (React UI)            │
│                                                  │
│  ┌─────────────────┐  ┌──────────────────┐     │
│  │ Segment Table    │  │ Email Variant     │     │
│  │ + AI Intelligence│  │ Preview Cards     │     │
│  └─────────────────┘  └──────────────────┘     │
│                                                  │
│        [ ✅ Approve ]    [ ❌ Reject ]           │
└─────────────────────────────────────────────────┘
```

- Marketers review AI-generated segments and email variants
- **Segment Intelligence**: Expandable AI explanations for each segment
- **Approve** → triggers Phase 2 execution
- **Reject** → resets campaign to draft

---

## Phase 2: Execution & MAB Optimization (Loop)

```
                    ┌─────────────────────────────────┐
                    │     Optimization Loop (1-3x)     │
                    │                                   │
┌──────────┐    ┌──►┌──────────┐  ┌──────────┐  ┌──────────┐ │
│ Approved │    │   │Execution │─►│Analytics │─►│Optimization│ │
│ Strategy │────┘   │  Agent   │  │  Agent   │  │   Agent   │ │
└──────────┘        └──────────┘  └──────────┘  └─────┬────┘ │
                                                       │       │
                                        stop? ◄────────┘       │
                                          │                     │
                                    no ───┘── yes ──►──────────┘
                                          │
                                    ┌─────▼─────┐
                                    │  Insight   │
                                    │   Agent    │
                                    └────────────┘
                                          │
                                    Final Campaign
                                     Insights
```

| Agent | Purpose | Key Technique |
|-------|---------|---------------|
| **ExecutionAgent** | Dispatches emails via dynamic OpenAPI tools | LLM function-calling |
| **AnalyticsAgent** | Collects open/click rates per variant | Metric simulation |
| **OptimizationAgent** | Decides exploit vs. explore per segment | Multi-Armed Bandit (MAB) |
| **InsightAgent** | Converts raw metrics into marketing insights | Data-to-narrative |

### Multi-Armed Bandit (MAB) Strategy
- **Exploit**: Allocate ~70% traffic to the winning variant
- **Explore**: Test the other variant with ~30% traffic
- **Stop condition**: Click rate > 15% → optimization converges
- **Max loops**: 3 (configurable)

---

## Data Flow Summary

```
User Brief → [Brief Agent] → Parsed JSON
                                   ↓
                          [Segmentation Agent] → Segments
                                   ↓
                           [Strategy Agent] → Strategies  ← Historical Learnings
                                   ↓
                            [Content Agent] → Variants    ← Historical Learnings
                                   ↓
                        ════ HUMAN APPROVAL ════
                                   ↓
                          [Execution Agent] → API Calls
                                   ↓
                          [Analytics Agent] → Metrics
                                   ↓
                        [Optimization Agent] → MAB Decisions
                                   ↓  (loop 1-3x)
                           [Insight Agent] → Natural Language Insights
                                   ↓
                        Campaign Complete → Dashboard
```
