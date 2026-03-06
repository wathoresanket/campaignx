"""
Historical Learning Service
─────────────────────────────
Analyzes past campaign insights to extract recurring performance patterns.
Surfaces accumulated knowledge so the platform demonstrably learns over time.
"""

import json
import logging
from typing import List, Dict
from agents.base_agent import BaseAgent
from sqlalchemy.orm import Session
from models import CampaignInsight

logger = logging.getLogger(__name__)


class HistoricalLearningService(BaseAgent):
    """Uses BaseAgent's LLM capabilities combined with DB access for historical analysis."""

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    async def get_learnings(self) -> List[Dict[str, str]]:
        """
        Queries all past campaign insights, feeds them to the LLM,
        and extracts recurring patterns and actionable learnings.
        """
        all_insights = (
            self.db.query(CampaignInsight)
            .order_by(CampaignInsight.timestamp.desc())
            .all()
        )
        if not all_insights:
            return self._default_learnings()

        # Limit to 50 most recent to avoid token overflow
        insights_text = [
            {
                "campaign_id": ins.campaign_id,
                "segment": ins.segment_name,
                "insight": ins.insight_content,
            }
            for ins in all_insights[:50]
        ]

        prompt = f"""
        You are an expert marketing analyst reviewing historical campaign performance data.
        Below are insights gathered from past campaigns. Analyze them and extract 3-5 
        recurring patterns or actionable learnings.

        Each learning should be a concise, specific statement that can guide future campaigns.
        Focus on what worked best: timing, tone, emoji usage, segment preferences, etc.

        Past Campaign Insights:
        {json.dumps(insights_text, indent=2)}

        Output a JSON object with key "learnings" containing a list of objects:
        - "learning": string (the actionable insight)
        - "confidence": string ("high", "medium", or "low" based on how many data points support it)
        """
        try:
            result = await self._complete_json(prompt)
            return result.get("learnings", [])
        except Exception as e:
            logger.error(f"Historical learning generation failed: {e}")
            return self._default_learnings()

    def get_learning_context_string(self) -> str:
        """
        Synchronous method that builds a plain-text summary of past learnings
        for injecting into agent prompts. Uses raw insights directly (no LLM).
        """
        insights = (
            self.db.query(CampaignInsight)
            .order_by(CampaignInsight.timestamp.desc())
            .limit(20)
            .all()
        )
        if not insights:
            return ""

        lines = ["Historical Campaign Learning:"]
        lines.extend(f"- [{ins.segment_name}] {ins.insight_content}" for ins in insights)
        lines.append("\nUse these insights to inform your strategy and content generation.")
        return "\n".join(lines)

    @staticmethod
    def _default_learnings() -> List[Dict[str, str]]:
        """Default learnings when no past data exists."""
        return [
            {
                "learning": "No previous campaign data available yet. Run campaigns to start building learnings.",
                "confidence": "low",
            }
        ]
