"""
BriefProcessor — Parses natural-language briefs into structured JSON.
"""

import logging
from typing import Dict, Any
from engines.base_engine import BaseEngine
from schemas import BriefOutputSchema

logger = logging.getLogger(__name__)


class BriefProcessor(BaseEngine):

    async def run(self, brief_text: str) -> Dict[str, Any]:
        """Parses a natural language brief into structured campaign JSON."""
        prompt = f"""
        You are an expert marketing campaign analyzer for SuperBFSI. Parse the following natural language campaign brief into a structured JSON format.
        
        Identify the specific product being promoted. While this platform is often used for SuperBFSI's "XDeposit" term deposit, do NOT default to it if the user specifies a different product (e.g., Credit Card, Loan).
        
        If and ONLY if the brief is generic or specifically about term deposits for SuperBFSI without a product name, you may default to:
        - "product": "XDeposit Term Deposit"
        - "cta_url": "https://superbfsi.com/xdeposit/explore/"
        
        The JSON should have these precise keys:
        - "product": string, name of the product being promoted
        - "constraints": string, any specific rules (e.g., "don't skip inactive")
        - "target_segments": list of strings, the overall target audience
        - "tone": string, the tone of the communication
        - "optimization_goal": string, what metrics to optimize for (e.g., "click_rate", "open_rate")
        - "cta_url": string, the official call to action URL

        Brief to parse:
        "{brief_text}"
        """
        try:
            parsed_data = await self._complete_pydantic(prompt, BriefOutputSchema, temperature=0.2)
            return parsed_data.model_dump()
        except Exception as e:
            logger.error(f"BriefProcessor failed: {e}")
            raise
