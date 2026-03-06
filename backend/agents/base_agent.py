"""
Base Agent
──────────
Shared foundation for all CampaignX AI agents.
Centralizes the Groq LLM client initialization and the common JSON-completion
pattern so individual agents only define their prompts and parsing logic.

Uses the Groq API (free tier) via the OpenAI-compatible SDK.
"""

import json
import logging
from typing import Any, Dict
from openai import AsyncOpenAI
from config import settings

logger = logging.getLogger(__name__)


class BaseAgent:
    """
    Base class for all LLM-powered agents.
    Subclasses inherit the Groq client setup and can call `_complete_json()`
    for the standard "system=JSON, user=prompt" pattern used everywhere.
    """

    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        self.model = model

    async def _complete_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Sends a structured-JSON completion request via Groq.
        Returns the parsed JSON dict from the LLM response.
        """
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You output JSON only."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        return json.loads(response.choices[0].message.content)

    @staticmethod
    def _build_history_section(historical_context: str) -> str:
        """Returns a prompt fragment with historical learning, or empty string."""
        if not historical_context:
            return ""
        return f"\n\n{historical_context}"
