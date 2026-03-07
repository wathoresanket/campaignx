<p align="center">
  <h1 align="center">🚀 CampaignX</h1>
  <p align="center"><strong>Fully Autonomous AI Marketing Intelligence Platform</strong></p>
  <p align="center">
    <em>Explainable AI · Pydantic Schemas · Multi-Armed Bandit Loop · 100K Cohort Scale</em>
  </p>
</p>

---

## 📋 Table of Contents

1. [Project Overview](#1-project-overview)
2. [Building Beyond the Brief (Enterprise Level Scale)](#2-building-beyond-the-brief-enterprise-level-scale)
3. [The 8-Agent Modular Architecture](#3-the-8-agent-modular-architecture)
4. [Reinforcement Learning: MAB Optimization](#4-reinforcement-learning-mab-optimization)
5. [Strict Evaluation Compliance & Bonus Checks](#5-strict-evaluation-compliance--bonus-checks)
6. [Technology Stack](#6-technology-stack)
7. [Installation & Deployment](#7-installation--deployment)

---

## 1. Project Overview

**CampaignX** is an industrial-grade, fully autonomous AI multi-agent system built specifically for the InXiteOut FrostHack 2026 Case Competition. 

Designed for **SuperBFSI**, the platform completely automates the highly complex digital marketing campaign lifecycle. Rather than relying on simple, monolithic LLM prompt chains, CampaignX orchestrates an ecosystem of **8 specialized AI Agents**. They ingest spoken Voice UI briefs, execute heavily segmented strategies parsed natively into JSON, dynamically consume external `openapi.json` APIs independent of hardcoding, and relentlessly optimize demographic conversion via Reinforcement Learning Multi-Armed Bandit testing.

---

## 2. Building Beyond the Brief (Enterprise Level Scale)

Our core competitive advantage is that CampaignX isn't a chatbot script; it's robust, deterministic software engineering. We natively built five high-impact innovations that deeply exceed the competition parameters.

*   🎙️ **Voice-to-Text Native Dashboard:** Marketers bypass paragraphs entirely. We integrated the browser's native Webkit Speech Recognition, enabling real-time verbal dictation of strategic campaign goals directly into the `CampaignBriefAgent`'s context buffer.
*   🧠 **Cross-Campaign SQLite Memory Logging:** Standard A/B tests vanish. Our `HistoricalLearningService` captures successful MAB conversion patterns (e.g., "Senior Citizens respond highest to +0.25% at 9:00 AM") and commits them to an SQLite DB. New iterations inject this prior knowledge directly into system prompts, eliminating repeated failed experimentation.
*   🚀 **O(N) Massive Cohort Scaling:** Stuffing 100,000 JSON user profiles into an LLM inevitably induces token crashes. We decouple this: The LLM reads only demographic *distributions* to generate grouping rules mathematically. Then, a blazing-fast local Python function checks the 100K array instantly at algorithmic time complexity `O(N)`.
*   🛡️ **Autonomous 100-Call API Limiting Middleware:** We strictly adhere to the PDF's API limit warning. We engineered a custom internal tracker (`rate_limit_tracker.py`) acting as a Python middleware barrier. It forcefully intercepts and async-sleeps execution agents before they can beach limits, preventing 429 live demo crashes natively.
*   📊 **Segment Intelligence LLMs:** To counter the AI "Black Box" problem, we deploy a separate `SegmentIntelligenceService` strictly tasked with examining generated cohorts and outputting a human-readable, executive rationale detailing *why* the users were paired.

---

## 3. The 8-Agent Modular Architecture

CampaignX eliminates LLM hallucinations via strict structural layering utilizing **Pydantic v2 type validation**. Execution exists across two discrete phases gated securely by a **Human-in-the-loop** UI check.

### Phase 1: Strategic Planning (Pre-Approval Engine)
1. **`CampaignBriefAgent`:** Ingests Voice/Text strings and strictly structures them against a `BriefOutputSchema` layout.
2. **`SegmentationAgent` & `SegmentIntelligenceService`:** Computes clustering rules dynamically and renders plain-English executive explanations.
3. **`StrategyAgent`:** Synthesizes A/B temporal execution matrices (e.g. Schedule Send Times via array variables).
4. **`ContentAgent`:** Crafts distinct linguistic logic mappings based on demographic profiling. Includes explicitly checked emoji flags and SuperBFSI endpoint payload formatting constraints.
    *   🛑 **THE SAFETY DASHBOARD GATE:** All operations forcefully halt here. The marketer reviews the full JSON/UI array plan. If rejected via string input, the `AgentOrchestrator` embeds the corrective context and regenerates. If safely **Approved**, execution commences.

### Phase 2: Autonomous Tool Execution (MAB Loop)
5. **`ExecutionAgent`:** Accessing the `OpenAPILoader` and `DynamicToolRegistry`, this agent pulls SuperBFSI schemas *dynamically*. **Zero hardcoded endpoints exist in our code base**.
6. **`AnalyticsAgent`:** Live-fetches temporal engagement metric payloads tracking user clicks.
7. **`OptimizationAgent`:** Executes the Reinforcement loop mathematics via the `Llama 3` solver.
8. **`InsightAgent`:** The UI translator mapping pure performance integers back into analytical text logic constraints.

---

## 4. Reinforcement Learning: MAB Optimization

Traditional A/B testing is deeply flawed—wasting exactly 50% of targeted execution traffic on the losing variable structure. 

CampaignX seamlessly integrates a programmatic Multi-Armed Bandit (MAB) Reinforcement Learning loop actively constructed around the FrostHack mathematical mandate:

**The Algorithmic Equation:** `Score = (0.7 × Click Rate) + (0.3 × Open Rate)`

```mermaid
flowchart TD
    classDef math fill:#8b5cf6,color:#fff,rx:8px,ry:8px,stroke:#5b21b6,stroke-width:2px;
    classDef decision fill:#ec4899,color:#fff,rx:8px,ry:8px,stroke:#be185d,stroke-width:2px;

    Metrics[Fetch Real-Time API Metrics] --> Calc[Apply Math Formula<br/><b>Score = (0.7 * Clicks) + (0.3 * Opens)</b>]:::math
    Calc --> Decision{Clear Winner<br>Identified?}:::decision
    Decision -- Yes (Exploit) --> Route[<b>Exploit Mode:</b> Route 80% Future Traffic<br/>To Output Variant]
    Decision -- No (Explore) --> Mutate[<b>Explore Mode:</b> LLM Mutates Losing Variants<br/>Modify Tone, Emoji String, Temporal Frame]
```

---

## 5. Strict Evaluation Compliance & Bonus Checks

| Core Requirement / Bonus Request | The Technical Implementation Solution |
| :--- | :--- |
| **API Tool Modularity (Sec 5.2 / Red Flag)** | **True Runtime Discovery.** Real-time FastAPI `OpenAPILoader` dynamically maps external URL configurations against interpreted JSON specs. |
| **Human-in-the-Loop (Sec 6.5 / Red Flag)** | React Vite Dashboard forces synchronous agent block prior to async `ExecutionAgent` payload initiation. |
| **Explainable AI Logging (Bonus 10.3.1)** | The React UI surfaces the discrete `AgentReasoning` objects natively pushed via every component agent. |
| **Real-Time Dashboards (Bonus 10.3.2)** | Fully interactive DOM rendering via Recharts and Tailwind mapping time-series mathematical conversions. |
| **Cloud-Deployable Code (Bonus 10.3.3)** | Isolated logic. Python Uvicorn components strictly severed from the Node.js visualization state tree. |

---

## 6. Technology Stack

- **Reasoning Engines:** `Groq Llama 3.3 70B` (Semantic logic inference & Optimization maths array selection).
- **Backend Architecture:** Python 3.10+, FastAPI Framework (`asyncio` concurrent loops), Pydantic v2 (Strict LLM guardrails).
- **Relational Memory State:** SQLAlchemy ORM / SQLite Native Cache (Continuous historical convergence indexing).
- **Frontend App:** Event-driven UI deployment via React 18, Vite natively, Recharts DOM plotting, and TailwindCSS (For rich, accessible styling primitives).

---

## 7. Installation & Deployment

### Step 1. Python Backend Boot sequence
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env # Ensure your AI_KEY string is initialized
uvicorn main:app --reload --port 8000
```

### Step 2. React UI Spin-up
```bash
cd frontend
npm install
npm run dev
```

> **CORS Deployment Note:** If port `5173` is occupied via caching, Vite falls back to `5174`. The FastAPI backend CORS is structurally configured natively to accept origins dynamically from both domains.

---
*Architected and engineered meticulously by [Your Team Name] for InXiteOut FrostHack 2026.*
