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
        prompt = f"""
        You are an AI Optimization Agent for an email marketing system. 
        You use Multi-Armed Bandit (MAB) principles to analyze the performance metrics of the current campaign run and dictate the strategy for the next run.
        For each segment, decide the next action: exploit the winning variant, or explore new ones.
        Provide segment-level optimizations including adjusted send time, subject style, and emoji usage.

        Current Run Metrics:
        {json.dumps(curr_metrics, indent=2)}

        Output a JSON object with two keys:
        1. "decisions": a list of objects containing:
            - "segment_name": string
            - "best_variant": string (the highest performing variant label)
            - "highest_click_rate": float
            - "action": string (MAB action, e.g. 'exploit 70%, explore 30%')
            - "send_time_adjustment": string (e.g. 'move to morning')
            - "subject_style": string (e.g. 'more urgent')
            - "emoji_usage": string (e.g. 'increase emojis')
        2. "stop_optimization": boolean (true if click rate on best variant is very high, >15%, else false to continue learning)
        """
        try:
            return await self._complete_json(prompt)
        except Exception as e:
            logger.error(f"OptimizationAgent failed: {e}")
            raise
