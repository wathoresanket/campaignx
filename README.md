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
5. [Agent Explanations](#5-detailed-explanation-of-every-agent)
6. [Optimization Loop](#6-optimization-loop-explanation)
7. [Dynamic API Discovery](#7-dynamic-api-discovery)
8. [New Intelligence Features](#8-new-intelligence-features)
9. [Segment Intelligence](#9-segment-intelligence)
10. [Historical Campaign Learning](#10-historical-campaign-learning)
11. [Optimization Timeline Visualization](#11-optimization-timeline-visualization)
12. [Campaign Lifecycle Timeline](#12-campaign-lifecycle-timeline)
13. [Live Agent Activity Feed](#13-live-agent-activity-feed)
14. [Tech Stack](#14-tech-stack)
15. [Project Structure](#15-detailed-project-structure)
16. [Setup Instructions](#16-step-by-step-setup-instructions)
17. [Demo Walkthrough](#17-demo-walkthrough)
18. [Example Campaign Scenario](#18-example-campaign-scenario)
19. [Example AI Insights Output](#19-example-ai-insights-output)
20. [Design Decisions](#20-design-decisions)
21. [Future Improvements](#21-future-improvements)

---

## 1. Project Overview

**CampaignX** is an AI-powered multi-agent marketing automation platform that transforms a simple natural language campaign brief into a fully optimized, executed, and analyzed email marketing campaign — all with minimal human intervention.

The platform orchestrates **8 specialized AI agents** that collaborate in a pipeline:

1. **Parse** the campaign brief
2. **Segment** customers into micro-groups
3. **Strategize** send timing and A/B testing plans
4. **Generate** personalized email variants
5. **Await** human-in-the-loop approval
6. **Execute** campaigns via dynamic API discovery
7. **Analyze** real-time engagement metrics
8. **Optimize** using Multi-Armed Bandit algorithms
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
│  │                    Services Layer                            │    │
│  │  Campaign · Analytics · Optimization · Insight              │    │
│  │  Segment Intelligence · Historical Learning                 │    │
│  └─────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │               SQLAlchemy ORM + SQLite                       │    │
│  │  Campaigns · Segments · Variants · Runs · Metrics · Logs    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Brief (text/voice)
    ↓
CampaignBriefAgent → Structured JSON
    ↓
SegmentationAgent → Customer Micro-Segments
    ↓
StrategyAgent → Send Times + A/B Plans (+ Historical Learning)
    ↓
ContentAgent → Email Variants A/B (+ Historical Learning)
    ↓
[Human Approval Gate]
    ↓
ExecutionAgent → Dynamic API Dispatch
    ↓
AnalyticsAgent → Engagement Metrics
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
| SegmentationAgent | Customer segmenter | Parsed brief | Micro-segments |
| StrategyAgent | Campaign strategist | Segments + History | Send times, A/B plans |
| ContentAgent | Copywriter | Brief + Strategy + History | Email variants |
| ExecutionAgent | API executor | Approved strategy | Dispatch results |
| AnalyticsAgent | Metrics collector | Segments | Open/click rates |
| OptimizationAgent | MAB optimizer | Current metrics | Next-loop decisions |
| InsightAgent | Data analyst | All metrics | Natural language insights |

**Key Design Principles:**
- Each agent has a single responsibility
- Agents communicate through the orchestrator
- All agent actions are transparently logged
- Historical learning is injected into StrategyAgent and ContentAgent

---

## 5. Detailed Explanation of Every Agent

### CampaignBriefAgent
Accepts a natural language campaign brief (text or voice input) and uses GPT-4o-mini to extract structured fields: product, constraints, target segments, tone, optimization goals, and CTA URL.

### SegmentationAgent
Fetches the customer cohort data and uses AI to create 2-4 micro-segments based on demographics (age, gender, income), activity level, and past engagement. Each segment gets a descriptive name and a customer count.

### StrategyAgent
Determines the optimal send time and A/B testing plan for each segment. **Now enhanced with historical learning** — past campaign insights are injected into the prompt so the AI can leverage proven patterns.

### ContentAgent
Generates two email variants (A and B) per segment. Variant A is professional, Variant B uses emojis and concise formatting. **Uses historical learning** to write more effective copy based on what worked in past campaigns.

### ExecutionAgent
Uses **dynamic OpenAPI discovery** to load available API endpoints at runtime, then instructs GPT to select the appropriate API tools and generate payloads for campaign dispatch.

### AnalyticsAgent
Simulates (or collects in production) engagement metrics — open rates and click rates — for each segment and variant combination across optimization loops.

### OptimizationAgent
Implements **Multi-Armed Bandit (MAB)** optimization. Analyzes per-variant performance across loops and decides whether to exploit the winning variant or explore new approaches. Provides segment-level adjustments for send time, subject style, and emoji usage.

### InsightAgent
Compiles all raw metrics from all optimization loops and generates natural language insights. For example: *"Variant B with emoji subject line achieved 14% click rate for Young Professionals, outperforming Variant A by 3.2%."*

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
2. **Exploitation**: In later loops, the winning variant gets prioritized (e.g., 70% exploit, 30% explore)
3. **Stop Condition**: If click rate exceeds 15%, optimization stops early
4. **Adjustments**: Each loop can modify send time, subject style, and emoji usage based on performance data

---

## 7. Dynamic API Discovery

The ExecutionAgent uses **OpenAPI specification discovery** to dynamically load API endpoints at runtime:

1. Loads `openapi.json` specification file
2. Extracts available endpoints and their schemas
3. Registers endpoints as callable tools
4. GPT-4o-mini selects the appropriate tool and generates arguments
5. The tool registry executes the HTTP call

This means the system can **adapt to new APIs without code changes** — just update the OpenAPI spec.

---

## 8. New Intelligence Features

CampaignX v2 introduces five intelligence layers that transform the platform from a campaign executor into a **learning marketing intelligence system**.

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
- `services/segment_intelligence_service.py` aggregates segment demographics and performance metrics
- Uses GPT-4o-mini to generate concise 2-3 sentence explanations
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
4. GPT-4o-mini extracts recurring patterns and assigns confidence levels
5. Learnings are displayed on the campaign creation page

**Learning Injection:**
Historical context is also **injected into StrategyAgent and ContentAgent prompts**, so future campaigns are directly influenced by past performance:

```
Historical Campaign Learning:
- [young_professionals] Variant B with emoji outperformed by 3.2%
- [female_senior_citizens] Morning send times drove 12% higher open rates

Use these insights to inform strategy and email generation.
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

The timeline updates **dynamically** as each stage completes, using agent log data and campaign status to determine progress. Status icons: ✔ completed, ⏳ running, ○ pending.

---

## 13. Live Agent Activity Feed

**Location**: Dashboard Page (right column) and Approval Page

A real-time terminal-style panel showing agents working step-by-step:

```
⏳ [CampaignBriefAgent] Parsing campaign brief
✔ [CampaignBriefAgent] Parsed campaign brief into structured data
⏳ [SegmentationAgent] Creating micro-segments from customer cohort
✔ [SegmentationAgent] Created customer micro-segments
⏳ [StrategyAgent] Selecting optimal send times and A/B test plans
✔ [StrategyAgent] Generated segment strategies with historical learning
```

**Features:**
- Progressive log entries that appear as agents work
- Status icons: ✔ completed, ⏳ running, ⚠ error
- CSS fade-in animation for new entries
- Auto-scroll to latest entry
- "● Live" indicator when agents are actively running

---

## 14. Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI (Python) | REST API server |
| **AI/LLM** | OpenAI GPT-4o-mini | Agent reasoning |
| **Database** | SQLite + SQLAlchemy ORM | Persistent storage |
| **Frontend** | React 19 + Vite 7 | Web interface |
| **Styling** | Tailwind CSS 4 | Utility-first CSS |
| **Charts** | Recharts 3 | Data visualization |
| **Icons** | Lucide React | UI icons |
| **HTTP Client** | Axios | API communication |
| **Voice Input** | Web Speech API | Speech-to-text |

---

## 15. Detailed Project Structure

```
campaignx/
├── backend/
│   ├── main.py                         # FastAPI app entry point
│   ├── config.py                       # Environment configuration
│   ├── database.py                     # SQLAlchemy engine & session
│   ├── models.py                       # ORM models (Campaign, Segment, etc.)
│   ├── schemas.py                      # Pydantic request/response schemas
│   ├── requirements.txt                # Python dependencies
│   │
│   ├── agents/                         # AI Agent implementations
│   │   ├── campaign_brief_agent.py     # NLP brief parser
│   │   ├── segmentation_agent.py       # Customer micro-segmentation
│   │   ├── strategy_agent.py           # ★ Send time & A/B strategy (+ history)
│   │   ├── content_agent.py            # ★ Email variant generator (+ history)
│   │   ├── execution_agent.py          # Dynamic API executor
│   │   ├── analytics_agent.py          # Engagement metrics collector
│   │   ├── optimization_agent.py       # Multi-armed bandit optimizer
│   │   └── insight_agent.py            # Natural language insight generator
│   │
│   ├── api/
│   │   └── campaign_api.py             # ★ REST endpoints (+ new intelligence APIs)
│   │
│   ├── orchestrator/
│   │   └── agent_orchestrator.py       # ★ Pipeline orchestrator (+ progressive logging)
│   │
│   ├── services/
│   │   ├── campaign_service.py         # Campaign CRUD operations
│   │   ├── analytics_service.py        # Run & metrics management
│   │   ├── optimization_service.py     # Optimization state management
│   │   ├── insight_service.py          # Insight storage
│   │   ├── segment_intelligence_service.py  # ★ NEW: AI segment explanations
│   │   └── historical_learning_service.py   # ★ NEW: Cross-campaign learning
│   │
│   ├── custom_logging/
│   │   └── agent_logger.py             # ★ Agent action logger (+ status tracking)
│   │
│   └── tools/
│       ├── openapi.json                # OpenAPI specification
│       ├── openapi_loader.py           # Spec parser
│       └── dynamic_tool_registry.py    # Runtime tool execution
│
└── frontend/
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx                    # React entry point
        ├── App.jsx                     # Router & navigation
        ├── index.css                   # Global styles (Tailwind)
        ├── App.css                     # App-level styles
        │
        ├── api/
        │   └── backendClient.js        # Axios API client
        │
        ├── components/
        │   ├── AgentLogsPanel.jsx       # ★ Live agent activity feed (enhanced)
        │   ├── SegmentTable.jsx         # ★ Segment table (+ intelligence rows)
        │   ├── MetricsChart.jsx         # Bar chart for per-run metrics
        │   ├── EmailVariantCard.jsx     # Email preview card
        │   ├── OptimizationTimelineChart.jsx  # ★ NEW: Line chart across runs
        │   ├── CampaignTimeline.jsx     # ★ NEW: 9-stage lifecycle timeline
        │   └── HistoricalLearningPanel.jsx    # ★ NEW: Past campaign learnings
        │
        └── pages/
            ├── CampaignBriefPage.jsx    # ★ Campaign creation (+ learning panel)
            ├── ApprovalPage.jsx         # ★ Human review (+ segment intelligence)
            ├── DashboardPage.jsx        # ★ Analytics dashboard (+ timeline + chart)
            └── AgentLogsPage.jsx        # Global agent logs viewer
```

> ★ = Modified or new in this version

---

## 16. Step-by-Step Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key

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
# Edit .env and add your OPENAI_API_KEY

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

### Environment Variables

```bash
OPENAI_API_KEY=sk-your-openai-api-key
DATABASE_URL=sqlite:///./campaignx.db    # Optional, defaults to SQLite
```

---

## 17. Demo Walkthrough

### Step 1: Create a Campaign
Navigate to the home page. You'll see the **Historical Campaign Learnings** panel (populated after your first campaign). Type or speak a campaign brief:

> *"Run an email campaign for XDeposit offering 1% higher returns. Give 0.25% extra for female senior citizens. Optimize for CTR and open rate."*

Click **Generate Campaign Plan**.

### Step 2: Watch Agents Work
You're redirected to the **Approval Page**. Watch the **Live Agent Activity Feed** as agents work:
- CampaignBriefAgent parses the brief
- SegmentationAgent creates micro-segments
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

## 18. Example Campaign Scenario

**Brief Input:**
> "Launch email campaign for XDeposit fixed deposit product targeting senior citizens and young professionals. Female senior citizens get extra 0.25% returns. Use professional tone. Optimize for open rate and click rate."

**Agent Pipeline Result:**

| Stage | Output |
|-------|--------|
| Brief Parsed | Product: XDeposit, Tone: professional, Segments: [senior_citizens, young_professionals, female_senior_citizens] |
| Segments Created | 4 micro-segments with 2,500 to 15,000 customers each |
| Strategy Generated | Morning sends for seniors, evenings for professionals; emoji vs professional subject A/B test |
| Variants Generated | 8 email variants (2 per segment: A=professional, B=emoji/concise) |
| Execution | Campaign dispatched via discovered APIs |
| Optimization | 3 loops: click rate improved from 5.8% → 8.2% → 11.4% |
| Insights | "Variant B outperforms for young professionals," "Morning sends +12% for seniors" |

---

## 19. Example AI Insights Output

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

## 20. Design Decisions

### Why Multi-Agent Architecture?
Each agent has a single responsibility, making the system modular, testable, and easy to extend. New agents can be added without modifying existing ones.

### Why Multi-Armed Bandit over Simple A/B Testing?
MAB dynamically balances exploration (trying new approaches) and exploitation (using proven winners), leading to faster convergence on optimal strategies with less wasted traffic.

### Why Dynamic API Discovery?
The ExecutionAgent loads API endpoints from an OpenAPI spec at runtime, meaning the system can integrate with any service that provides an OpenAPI specification — without code changes.

### Why Historical Learning Injection?
Rather than just displaying past learnings, CampaignX **injects them directly into agent prompts**. This creates a genuine feedback loop where the system improves with each campaign.

### Why Progressive Agent Logs?
Rather than showing results only after completion, agents log "running" and "completed" states, creating a live activity feed that makes the AI reasoning process transparent and engaging.

### Why SQLite?
For a hackathon demonstration, SQLite provides zero-configuration persistence that works immediately without external services, while SQLAlchemy makes it trivial to switch to PostgreSQL for production.

---

## 21. Future Improvements

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
- **Agent Memory**: Long-term memory for agents to remember preferences and decisions across campaigns

---

<p align="center">
  <strong>Built with ❤️ for hackathon excellence</strong><br/>
  <em>CampaignX — Where AI meets marketing intelligence</em>
</p>
