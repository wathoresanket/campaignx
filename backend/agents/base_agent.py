"""
Base Agent
──────────
Shared foundation for all CampaignX AI agents.
Uses Groq API for ultra-fast completions.
"""

import json
import logging
import asyncio
from typing import Any, Dict, Type, TypeVar
from groq import AsyncGroq
from pydantic import BaseModel, ValidationError
from config import settings

logger = logging.getLogger(__name__)

# Type definition for generic Pydantic models
ModelType = TypeVar('ModelType', bound=BaseModel)

# Configure globally
groq_client = None
if settings.GROQ_API_KEY:
    groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)


class BaseAgent:
    """
    Base class for all intelligent agents.
    Uses Groq API.
    Subclasses inherit the client and call `_complete_json()`.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        self.model = model

    async def _complete_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Sends a structured-JSON completion request via Groq.
        Returns the parsed JSON dict from the completion response.
        """
        if not groq_client:
            raise ValueError("GROQ_API_KEY is not configured in .env")
            
        try:
            # Groq's JSON mode requires the prompt to include "json"
            if "json" not in prompt.lower():
                prompt += "\n\nImportant: You must reply in valid JSON format."
                
            response = await asyncio.wait_for(
                groq_client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    response_format={"type": "json_object"}
                ),
                timeout=30.0
            )
            return json.loads(response.choices[0].message.content)
        except asyncio.TimeoutError:
            logger.error("Groq API call timed out after 30 seconds.")
            raise Exception("Groq API call timed out.")
        except Exception as e:
            logger.error(f"Groq API generation failed: {e}")
            raise

    async def _complete_pydantic(self, prompt: str, schema: Type[ModelType], temperature: float = 0.3) -> ModelType:
        """
        Sends a completion request and enforces the given Pydantic schema over the output.
        Automatically retries once if the initial output is malformed.
        """
        # Pydantic v2 support
        schema_json = schema.model_json_schema() if hasattr(schema, "model_json_schema") else schema.schema()
        
        # Enforce exact JSON rules
        instruction = f"\n\nYou MUST reply in exactly this JSON schema format. Do not wrap in markdown.\nJSON Schema details: {json.dumps(schema_json)}"
        full_prompt = prompt + instruction

        try:
            # Try once
            raw_dict = await self._complete_json(full_prompt, temperature)
            return schema(**raw_dict) if not hasattr(schema, "model_validate") else schema.model_validate(raw_dict)
            
        except (ValidationError, json.JSONDecodeError) as e:
            logger.warning(f"Initial response failed structure validation. Retrying once. Error: {e}")
            
            # Retry Once
            retry_prompt = f"{full_prompt}\n\nWARNING: Your previous response failed validation with error: {e}. Please correct it and output raw JSON ONLY."
            raw_dict_retry = await self._complete_json(retry_prompt, temperature)
            return schema(**raw_dict_retry) if not hasattr(schema, "model_validate") else schema.model_validate(raw_dict_retry)

    @staticmethod
    def _build_history_section(historical_context: str) -> str:
        """Returns a prompt fragment with historical learning, or empty string."""
        if not historical_context:
            return ""
        return f"\n\n{historical_context}"
