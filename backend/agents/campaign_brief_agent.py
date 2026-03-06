"""
CampaignBriefAgent — Parses natural-language briefs into structured JSON.
"""

import logging
from typing import Dict, Any
from agents.base_agent import BaseAgent
from schemas import BriefOutputSchema

logger = logging.getLogger(__name__)


class CampaignBriefAgent(BaseAgent):

    async def run(self, brief_text: str) -> Dict[str, Any]:
        """Parses a natural language brief into structured campaign JSON."""
        prompt = f"""
        You are an expert marketing campaign analyzer. Parse the following natural language campaign brief into a structured JSON format.
        
        The JSON should have these precise keys:
        - "product": string, name of the product being promoted
        - "constraints": string, any specific rules or constraints mentioned
        - "target_segments": list of strings, the overall target audience mentioned
        - "tone": string, the tone of the communication
        - "optimization_goal": string, what metrics to optimize for (e.g., "open rate and click rate")
        - "cta_url": string, the call to action URL if present, otherwise null

        Brief to parse:
        "{brief_text}"
        """
        try:
            parsed_data = await self._complete_pydantic(prompt, BriefOutputSchema, temperature=0.2)
            return parsed_data.model_dump()
        except Exception as e:
            logger.error(f"CampaignBriefAgent failed: {e}")
            raise
