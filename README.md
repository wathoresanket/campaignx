<p align="center">
  <h1 align="center">🚀 CampaignX</h1>
  <p align="center"><strong>Integrated Marketing Intelligence Platform</strong></p>
  <p align="center">
    <em>Deep Analytics · Structural Validation · Adaptive Optimization · Large-Scale Cohort Processing</em>
  </p>
</p>

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Advanced Scale Engineering](#2-advanced-scale-engineering)
3. [Modular Logic Architecture](#3-modular-logic-architecture)
4. [Adaptive Optimization Engine](#4-adaptive-optimization-engine)
5. [Enterprise Compliance & Validation](#5-enterprise-compliance--validation)
6. [Technology Stack](#6-technology-stack)
7. [Installation & Deployment](#7-installation--deployment)

---

## 1. Project Overview

**CampaignX** is an industrial-grade marketing automation platform built specifically for the InXiteOut FrostHack 2026 Case Competition. 

**📢 FINAL ON-CAMPUS ROUND UPDATE:** 
All preliminary campaign data has been reset. CampaignX is now configured for the **Final Evaluation Phase** (09 March 11:59 PM — 14 March 11:59 PM). The system operates on a new cohort of **1,000 customers** fetched dynamically via the `get_customer_cohort` API.

Designed for **SuperBFSI**, the platform automates the complex digital marketing campaign lifecycle. CampaignX orchestrates an ecosystem of **specialized Processing Engines**. They ingest spoken Voice UI briefs, execute heavily segmented strategies parsed into structured data, dynamically consume external `openapi.json` APIs, and relentlessly optimize demographic conversion via Adaptive Reward testing.

---

## 2. Advanced Scale Engineering

Our core competitive advantage is robust, deterministic software engineering. We natively built high-impact innovations that meet enterprise requirements.

*   🎙️ **Voice-to-Text Native Dashboard:** Marketers can dictate strategic goals directly into the system. We integrated the browser's native Webkit Speech Recognition for real-time verbal dictation.
*   🧠 **Cross-Campaign Analytics Persistence:** Successful conversion patterns (e.g., "Senior Citizens respond highest to +0.25% at 9:00 AM") are captured and stored in an SQLite DB to inform future strategy iterations.
*   🚀 **High-Performance Cohort Scaling:** To handle large datasets efficiently, we decouple demographic analysis from cohort execution. The system defines grouping rules mathematically and uses optimized local functions for instant processing.
*   🛡️ **Rate-Limit Management Middleware:** We strictly adhere to API usage limits. A custom `rate_limit_tracker.py` acts as an async barrier to prevent service interruptions during high-load operations.
*   📊 **Segment Intelligence Dashboard:** To ensure operational transparency, we deploy a `SegmentIntelligenceService` that provides detailed rationale for customer grouping and campaign strategy.

---

## 3. Modular Logic Architecture

CampaignX ensures high reliability via strict structural layering utilizing **Pydantic v2 type validation**. Execution exists across two discrete phases gated by a **Human-in-the-loop** check.

### Phase 1: Strategic Planning (Configuration Engine)
1. **`BriefProcessor`:** Structures natural language input into validated campaign parameters.
2. **`SegmentEngine`:** Generates classification rules and provides analytical rationale.
3. **`StrategyEngine`:** Synthesizes temporal execution matrices and A/B test patterns.
4. **`ContentEngine`:** Crafts linguistic variations based on demographic profiling and SuperBFSI payload constraints.
    *   🛑 **APPROVAL GATE:** The system halts here for human review. Marketers inspect the full campaign plan. If the plan requires adjustments, the coordinator incorporates feedback and regenerates.

### Phase 2: Automated Execution (Optimization Loop)
5. **`ExecutionEngine`:** Utilizing a dynamic tool discovery system, this engine interfaces with SuperBFSI endpoints without hardcoded configurations.
6. **`AnalyticsEngine`:** Aggregates real-time engagement data tracking user interactions.
7. **`OptimizationEngine`:** Executes adaptive reward logic to refine current campaign performance.
8. **`InsightEngine`:** Translates performance metrics into actionable strategic findings.

---

## 4. Adaptive Optimization Engine

CampaignX integrates a programmatic Adaptive Learning loop constructed around the FrostHack Scoring mandate:

**Primary Scoring Criterion:** Maximizing the total count of **'Email Clicked' (EC = Y)** and **'Email Opened' (EO = Y)**.

**The Algorithmic Equation:** `Score = (0.7 × Click Rate) + (0.3 × Open Rate)`

```mermaid
flowchart TD
    classDef math fill:#8b5cf6,color:#fff,rx:8px,ry:8px,stroke:#5b21b6,stroke-width:2px;
    classDef decision fill:#ec4899,color:#fff,rx:8px,ry:8px,stroke:#be185d,stroke-width:2px;

    Metrics[Fetch Real-Time API Metrics] --> Calc[Apply Scoring Formula<br/><b>Score = (0.7 * Clicks) + (0.3 * Opens)</b>]:::math
    Decision{Optimization<br>Threshold Met?}:::decision
    Calc --> Decision
    Decision -- Yes (Exploit) --> Route[<b>Direct Traffic:</b> Route Higher Proportion<br/>To Winning Variant]
    Decision -- No (Explore) --> Mutate[<b>Refine Strategy:</b> Adjust Tone, Meta-Tags,<br/>and Delivery Windows]
```

---

## 5. Enterprise Compliance & Validation

| Core Requirement | Technical Implementation |
| :--- | :--- |
| **API Tool Modularity** | **Dynamic Endpoint Discovery.** Real-time `OpenAPILoader` maps URL configurations against interpreted JSON specs. |
| **Human-in-the-Loop** | Built-in approval workflow prevents unauthorized automated execution. |
| **Transparency & Logging** | The dashboard surfaces detailed internal logic and decision flows. |
| **Real-Time Visualization** | Interactive reporting via time-series processing and data visualization. |
| **Modular Deployment** | Clean separation between processing core and visualization layer. |

---

## 6. Technology Stack

- **Logical Processing:** Advanced Language Modeling via `Llama 3.3` (Semantic inference & logic selection).
- **Backend Architecture:** Python 3.10+, FastAPI Framework (`asyncio` concurrency), Pydantic v2 (Strict validation).
- **Relational Persistence:** SQLAlchemy ORM / SQLite (Continuous historical indexing).
- **Frontend Layer:** React 18, Vite, Recharts, and TailwindCSS (For rich, accessible interface components).

---

## 7. Installation & Deployment

### Step 1. Backend Boot Sequence
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env 
uvicorn main:app --reload --port 8000
```

### Step 2. Visualization UI Spin-up
```bash
cd frontend
npm install
npm run dev
```

> **CORS Deployment Note:** If port `5173` is occupied via caching, Vite falls back to `5174`. The FastAPI backend CORS is structurally configured natively to accept origins dynamically from both domains.

---
*Architected and engineered meticulously for InXiteOut FrostHack 2026.*
