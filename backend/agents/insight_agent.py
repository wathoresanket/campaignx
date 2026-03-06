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
        You are an expert marketing data analyst. Review the automated campaign metrics below and generate 1-2 powerful insights per segment.
        A good insight points out what performed best (send time, tone, emoji usage) and calculates differences or wins (e.g., 'Best Email Variant: B', 'Top Click Rate: 14%').
        
        Metrics:
        {json.dumps(metrics, indent=2)}
        
        Output a JSON object with the key "insights", which is a list of objects containing:
        - "segment_name": string
        - "insight_content": string (the human readable insight summarizing the best variant and performance)
        """
        try:
            result = await self._complete_json(prompt)
            return result.get("insights", [])
        except Exception as e:
            logger.error(f"InsightAgent failed: {e}")
            raise
