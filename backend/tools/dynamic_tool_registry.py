import httpx
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DynamicToolRegistry:
    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers)
        self._registry = {}
        
    def register_tool(self, name: str, path: str, method: str):
        """Registers a dynamic tool handler."""
        async def handler(**kwargs):
            logger.info(f"Executing dynamic tool {name} -> {method.upper()} {path} with args {kwargs}")
            try:
                if method.lower() == "post":
                    resp = await self.client.post(path, json=kwargs)
                elif method.lower() == "get":
                    resp = await self.client.get(path, params=kwargs)
                else:
                    return {"error": "Unsupported method"}
                
                return resp.json()
            except Exception as e:
                logger.error(f"Error executing {name}: {e}")
                return {"error": str(e)}
                
        self._registry[name] = handler
        
    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        if tool_name not in self._registry:
            raise ValueError(f"Tool {tool_name} not found in registry.")
        
        handler = self._registry[tool_name]
        return await handler(**arguments)
