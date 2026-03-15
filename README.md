# 🚀 CampaignX
**Integrated Marketing Intelligence Platform**

*Deep Analytics · Structural Validation · Adaptive Optimization · Large-Scale Cohort Processing*

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

**CampaignX** is an industrial-grade marketing automation platform designed to streamline complex digital marketing campaigns.

The platform automates the digital marketing campaign lifecycle by orchestrating an ecosystem of **specialized Processing Engines**. They ingest strategy briefs, execute segmented strategies parsed into structured data, dynamically consume external APIs, and optimize conversion via Adaptive Learning.

---

## 2. Advanced Scale Engineering

Our core advantage is robust, deterministic software engineering, featuring high-impact innovations that meet enterprise requirements.

*   🎙️ **Voice-to-Text Native Dashboard:** Marketers can dictate strategic goals directly into the system using integrated real-time verbal dictation.
*   🧠 **Cross-Campaign Analytics Persistence:** Successful conversion patterns are captured and stored in an SQLite DB to inform future strategy iterations.
*   🚀 **High-Performance Cohort Scaling:** Decouples demographic analysis from cohort execution using optimized processing for large datasets.
*   🛡️ **Rate-Limit Management Middleware:** Custom async barriers prevent service interruptions during high-load operations.
*   📊 **Segment Intelligence Dashboard:** Provides transparency with detailed rationale for customer grouping and campaign strategy.

---

## 3. Modular Logic Architecture

CampaignX ensures high reliability via strict structural layering utilizing **Pydantic v2 type validation**. Execution exists across two discrete phases gated by a **Human-in-the-loop** check.

---

## 4. Adaptive Optimization Engine

CampaignX integrates a programmatic Adaptive Learning loop focused on maximizing engagement:

**Primary Metrics:** Maximizing the total count of **'Email Clicked'** and **'Email Opened'**.

**The Algorithmic Equation:** `Score = (0.7 × Click Rate) + (0.3 × Open Rate)`

---

## 5. Enterprise Compliance & Validation

| Core Requirement | Technical Implementation |
| :--- | :--- |
| **API Tool Modularity** | **Dynamic Endpoint Discovery.** Real-time mapping against interpreted JSON specs. |
| **Human-in-the-Loop** | Built-in approval workflow prevents unauthorized automated execution. |
| **Transparency & Logging** | Dashboard surfaces detailed internal logic and decision flows. |
| **Real-Time Visualization** | Interactive reporting via time-series processing and data visualization. |
| **Modular Deployment** | Clean separation between processing core and visualization layer. |

---

## 6. Technology Stack

- **Logical Processing:** Advanced Language Modeling (Semantic inference & logic selection).
- **Backend Architecture:** Python 3.10+, FastAPI Framework (`asyncio` concurrency), Pydantic v2 (Strict validation).
- **Relational Persistence:** SQLAlchemy ORM / SQLite (Continuous historical indexing).
- **Frontend Layer:** React 18, Vite, Recharts, and TailwindCSS.

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

> **CORS Deployment Note:** If port `5173` is occupied, Vite falls back to `5174`. The FastAPI backend CORS is configured to accept origins dynamically from both domains.

---
*Architected and engineered meticulously for CampaignX.*
