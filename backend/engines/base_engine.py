"""
Base Engine
───────────
Shared foundation for all CampaignX processing engines.
Uses Groq connectivity for ultra-fast logical processing.
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


class BaseEngine:
    """
    Base class for all processing engines.
    Uses Groq API.
    Subclasses inherit the client and call `_complete_json()`.
    """

    def __init__(self, model: str = "llama-3.1-8b-instant"):
        self.model = model

    async def _complete_json(self, prompt: str, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Sends a structured-JSON completion request via Groq.
        Returns the parsed JSON dict from the completion response.
        """
        if not groq_client:
            raise ValueError("GROQ_API_KEY is not configured in .env")
            
        max_retries = 3
        base_delay = 5  # Start with 5s delay for 429s
        
        for attempt in range(max_retries + 1):
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
                    timeout=60.0
                )

                # Small throttle to stay within Groq free-tier rate limits
                await asyncio.sleep(2)

                return json.loads(response.choices[0].message.content)
            
            except asyncio.TimeoutError:
                logger.error(f"Groq API call timed out (Attempt {attempt+1}/{max_retries+1})")
                if attempt == max_retries:
                    raise Exception("Groq API call timed out after multiple retries.")
                await asyncio.sleep(base_delay * (2 ** attempt))
                
            except Exception as e:
                # Check for rate limit error (429)
                error_msg = str(e).lower()
                if "rate limit" in error_msg or "429" in error_msg:
                    logger.warning(f"Groq Rate Limit hit (Attempt {attempt+1}/{max_retries+1}). Retrying in {base_delay * (2 ** attempt)}s...")
                    if attempt == max_retries:
                        raise e
                    await asyncio.sleep(base_delay * (2 ** attempt))
                else:
                    logger.error(f"Groq API generation failed: {e}")
                    raise
        
        raise Exception("Failed to generate response after multiple retries.")

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
