"""
StrategyAgent — Determines optimal send times and A/B testing plans per segment.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List
from agents.base_agent import BaseAgent
from schemas import StrategyOutputSchema

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

class StrategyAgent(BaseAgent):

    async def run(self, segments: List[Dict[str, Any]], historical_context: str = "") -> List[Dict[str, Any]]:
        """
        Determines the optimal send time and A/B testing plan per segment.
        Optionally uses historical campaign learnings to inform decisions.
        """
        history = self._build_history_section(historical_context)

        # Strip customer_ids to keep prompt small — LLM only needs segment metadata
        slim_segments = [
            {k: v for k, v in seg.items() if k != "customer_ids"}
            for seg in segments
        ]
        
        async def _generate_for_segment(segment: Dict[str, Any]) -> Dict[str, Any]:
            prompt = f"""
            You are an expert marketing strategist. Given the following customer segment, 
            determine an optimal send time, the number of variants (max 2), and a brief A/B testing plan.

            IMPORTANT: send_time MUST be in DD:MM:YY HH:MM:SS format (IST), e.g. "06:03:26 09:00:00".

            Segment:
            {json.dumps(segment, indent=2)}
            {history}
            Return a JSON object:
            - "segment_name": string
            - "send_time": string in DD:MM:YY HH:MM:SS format (e.g. "06:03:26 09:00:00")
            - "variants_count": integer (always 2 for A/B testing)
            - "ab_testing_plan": short description of what to test (e.g. "Test emoji subject vs professional subject")
            """
            try:
                parsed_strategy = await self._complete_pydantic(prompt, StrategyOutputSchema, temperature=0.2)
                return parsed_strategy.model_dump()
            except Exception as e:
                logger.error(f"StrategyAgent failed for segment {segment.get('name')}: {e}")
                return {
                    "segment_name": segment.get("name", "Unknown"),
                    "send_time": "12:12:26 10:00:00",
                    "variants_count": 2,
                    "ab_testing_plan": "Default A/B Test"
                }

        tasks = [_generate_for_segment(seg) for seg in slim_segments]
        
        if tasks:
            results = await asyncio.gather(*tasks)
            return list(results)
            
        return []
