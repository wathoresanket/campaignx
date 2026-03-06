"""
OptimizationAgent — Multi-Armed Bandit optimizer for campaign performance.
"""

import json
import logging
from typing import Dict, Any, List
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class OptimizationAgent(BaseAgent):

    async def run(self, curr_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes current run metrics using MAB principles.
        Returns optimization decisions for the next loop.
        """
        # Strip any large nested data from metrics before sending to LLM
        slim_metrics = []
        for m in curr_metrics:
            slim_metrics.append({
                k: v for k, v in m.items()
                if k not in ("customer_ids", "report_data", "raw_data")
            })

        prompt = f"""
        You are an AI Optimization Agent for email marketing using Multi-Armed Bandit (MAB) principles.
        Analyze these metrics and decide the next action per segment: exploit the winning variant (~70%) or explore (~30%).

        Current Run Metrics:
        {json.dumps(slim_metrics, indent=2)}

        Output a JSON object with two keys:
        1. "decisions": a list of objects containing:
            - "segment_name": string
            - "best_variant": string (highest performing variant label)
            - "highest_click_rate": float
            - "action": string (e.g. "exploit 70%, explore 30%")
            - "send_time_adjustment": string (e.g. "move to morning")
            - "subject_style": string (e.g. "more urgent")
            - "emoji_usage": string (e.g. "increase emojis")
        2. "stop_optimization": boolean (true if best click rate > 15%, else false)
        """
        try:
            return await self._complete_json(prompt)
        except Exception as e:
            logger.error(f"OptimizationAgent failed: {e}")
            raise
