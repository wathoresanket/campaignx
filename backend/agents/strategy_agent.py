"""
StrategyAgent — Determines optimal send times and A/B testing plans per segment.
"""

import json
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class StrategyAgent(BaseAgent):

    async def run(self, segments: List[Dict[str, Any]], historical_context: str = "") -> List[Dict[str, Any]]:
        """
        Determines the optimal send time and A/B testing plan per segment.
        Optionally uses historical campaign learnings to inform decisions.
        """
        history = self._build_history_section(historical_context)

        prompt = f"""
        You are an expert marketing strategist. Given the following customer segments, 
        determine an optimal send time, the number of variants (max 2), and a brief A/B testing plan for each segment.

        Segments:
        {json.dumps(segments, indent=2)}
        {history}
        Return a JSON object with a key "strategies" which is a list.
        Each item in the list should match the segment name and include:
        - "segment_name": string
        - "send_time": optimal send time (e.g. "09:00 AM", "06:00 PM")
        - "variants_count": integer (always 2 for A/B testing)
        - "ab_testing_plan": short description of what to test (e.g. "Test emoji subject vs professional subject")
        """
        try:
            result = await self._complete_json(prompt, temperature=0.2)
            return result.get("strategies", [])
        except Exception as e:
            logger.error(f"StrategyAgent failed: {e}")
            raise

    def _mock_response(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [
            {
                "segment_name": seg["name"],
                "send_time": "10:00 AM" if i % 2 == 0 else "08:00 PM",
                "variants_count": 2,
                "ab_testing_plan": "Test emoji subject vs professional subject",
            }
            for i, seg in enumerate(segments)
        ]
