"""
InsightAgent — Generates natural-language marketing insights from campaign metrics.
"""

import json
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class InsightAgent(BaseAgent):

    async def run(self, metrics: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Takes raw metrics across optimization loops and converts them
        into human-readable marketing insights per segment.
        """
        prompt = f"""
        You are an expert marketing data analyst. Review the automated campaign metrics below and generate powerful, highly structured insights per segment.
        A good insight points out exactly what performed best (send time, tone, subject pattern) and calculates wins (e.g. 'Best Email Variant: B', 'Top Click Rate: 14%').
        
        Metrics:
        {json.dumps(metrics, indent=2)}
        
        Provide the following details for each segment:
        - top_segment: What demographic or profile this specific segment represents
        - winning_subject_pattern: What specific phrase, style, or inclusion made the best subject line win
        - best_send_time: Optimal delivery time discovered
        - key_insight: A 1-2 sentence human-readable takeaway summarizing performance
        - recommendation: What to do in the next campaign for this segment
        """
        try:
            from schemas import InsightsOutputSchema
            result = await self._complete_pydantic(prompt, InsightsOutputSchema)
            return [insight.model_dump() for insight in result.insights]
        except Exception as e:
            logger.error(f"InsightAgent failed: {e}")
            raise
