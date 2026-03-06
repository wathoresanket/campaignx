"""
Segment Intelligence Service
─────────────────────────────
Analyzes segment demographics and engagement metrics to generate
human-readable explanations for each customer segment using LLM analysis.
"""

import json
import logging
from typing import Dict, List
from agents.base_agent import BaseAgent
from sqlalchemy.orm import Session
from models import Campaign, Segment, PerformanceMetric

logger = logging.getLogger(__name__)


class SegmentIntelligenceService(BaseAgent):
    """Uses BaseAgent's LLM capabilities to generate segment intelligence."""

    def __init__(self, db: Session):
        super().__init__()
        self.db = db

    async def generate_intelligence(self, campaign_id: int) -> List[Dict[str, str]]:
        """
        Generates human-readable intelligence for each segment in a campaign.
        Combines segment info with performance metrics to produce actionable insights.
        """
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return []

        segments = self.db.query(Segment).filter(Segment.campaign_id == campaign_id).all()
        if not segments:
            return []

        segment_data = self._gather_segment_data(segments)

        prompt = f"""
        You are an expert marketing analyst. For each customer segment below, 
        generate a concise, actionable intelligence summary (2-3 sentences).
        
        Explain what makes this segment unique, their engagement patterns, 
        and the best marketing approach for them.

        Campaign Product: {campaign.product or 'Unknown'}
        Campaign Tone: {campaign.tone or 'professional'}
        
        Segments:
        {json.dumps(segment_data, indent=2)}

        Output a JSON object with key "intelligence" containing a list of objects:
        - "segment_name": string
        - "intelligence": string (the human-readable explanation)
        """
        try:
            result = await self._complete_json(prompt)
            return result.get("intelligence", [])
        except Exception as e:
            logger.error(f"Segment intelligence generation failed: {e}")
            return self._fallback_intelligence(segment_data)

    def _gather_segment_data(self, segments) -> list:
        """Collects segment info with averaged performance metrics."""
        data = []
        for seg in segments:
            metrics = self.db.query(PerformanceMetric).filter(
                PerformanceMetric.segment_id == seg.id
            ).all()

            avg_open = sum(m.open_rate for m in metrics) / len(metrics) if metrics else 0.0
            avg_click = sum(m.click_rate for m in metrics) / len(metrics) if metrics else 0.0

            data.append({
                "name": seg.name,
                "customer_count": seg.customer_count,
                "avg_open_rate": round(avg_open, 4),
                "avg_click_rate": round(avg_click, 4),
                "has_metrics": len(metrics) > 0,
            })
        return data

    @staticmethod
    def _fallback_intelligence(segment_data: list) -> List[Dict[str, str]]:
        """Fallback intelligence when LLM is unavailable."""
        results = []
        for seg in segment_data:
            name = seg["name"].replace("_", " ").title()
            intel = f"{name} segment contains {seg['customer_count']:,} customers."
            if seg["has_metrics"]:
                intel += f" Average open rate: {seg['avg_open_rate']*100:.1f}%, click rate: {seg['avg_click_rate']*100:.1f}%."
            else:
                intel += " No engagement data available yet — metrics will appear after campaign execution."
            results.append({"segment_name": seg["name"], "intelligence": intel})
        return results
