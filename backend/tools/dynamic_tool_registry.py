"""
DynamicToolRegistry
───────────────────
Dynamically registers and executes API tools discovered from an OpenAPI specification.
Uses X-API-Key header authentication matching the CampaignX API.
"""

import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class DynamicToolRegistry:
    """
    Registers API endpoints as callable tools and executes them via HTTP.
    Built on top of OpenAPILoader — each tool corresponds to an operation
    discovered from the OpenAPI spec at runtime.
    """

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self._registry: Dict[str, Any] = {}

    def _client(self) -> httpx.AsyncClient:
        """Creates a new async HTTP client with proper auth headers."""
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0,
        )

    def register_tool(self, name: str, path: str, method: str):
        """Registers a dynamic tool handler discovered from the OpenAPI spec."""
        self._registry[name] = {"path": path, "method": method.lower()}
        logger.info(f"Registered dynamic tool: {name} → {method.upper()} {path}")

    def get_registered_tools(self) -> list:
        """Returns list of registered tool names."""
        return list(self._registry.keys())

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Executes a registered tool by making the corresponding HTTP request.
        POST endpoints receive arguments as JSON body.
        GET endpoints receive arguments as query parameters.
        """
        if tool_name not in self._registry:
            raise ValueError(f"Tool '{tool_name}' not found. Available: {self.get_registered_tools()}")

        tool = self._registry[tool_name]
        path = tool["path"]
        method = tool["method"]

        logger.info(f"Executing dynamic tool: {tool_name} → {method.upper()} {path}")

        async with self._client() as client:
            try:
                if method == "post":
                    resp = await client.post(path, json=arguments)
                elif method == "get":
                    resp = await client.get(path, params=arguments)
                else:
                    return {"error": f"Unsupported HTTP method: {method}"}

                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error executing {tool_name}: {e.response.status_code} — {e.response.text}")
                return {"error": str(e), "status_code": e.response.status_code}
            except Exception as e:
                logger.error(f"Error executing {tool_name}: {e}")
                return {"error": str(e)}
