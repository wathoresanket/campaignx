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
        - "key_benefits": list of strings, Summary of ALL factual benefits.
        - "global_benefits": list of strings, Benefits that apply to EVERYONE (e.g. "1% interest"). IMPORTANT: Every benefit mentioned in the brief must be categorized here if it applies to all users.
        - "conditional_benefits": list of strings, Demographic-specific bonuses (e.g. "+0.25% for seniors"). IMPORTANT: Clearly separate targeted rewards from general ones. Do NOT overlap with global_benefits.
        - "special_conditions": string, other campaign rules.

        PEDANTIC PARSING RULES:
        1. If a benefit is linked to a demographic (e.g. "seniors", "students", "female", "under 25"), it MUST go into `conditional_benefits`.
        2. If it's available to anyone opening the account, it MUST go into `global_benefits`.
        3. EXTRACT TARGET SEGMENTS: You MUST scan the brief for ANY mention of specific audiences.
            - Any group mentioned in `conditional_benefits` (e.g., "female senior citizens") MUST be added to `target_segments`.
            - Any group mentioned in `constraints` (e.g., "don't skip inactive" -> "inactive customers") MUST be added to `target_segments`.
            - Do NOT just put "all customers" if specific groups are mentioned. You can include "all customers" as the broad audience, but specific groups MUST be listed separately.
        
        Accuracy is critical to prevent false claims for ineligible segments and to ensure the Segmentation Engine creates the right rules.

        Brief to parse:
        "{brief_text}"
        """
        try:
            parsed_data = await self._complete_pydantic(prompt, BriefOutputSchema, temperature=0.2)
            return parsed_data.model_dump()
        except Exception as e:
            logger.error(f"BriefProcessor failed: {e}")
            raise
