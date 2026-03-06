import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class OpenAPILoader:
    def __init__(self, spec_path_or_url: str):
        self.spec = self._load_spec(spec_path_or_url)
        
    def _load_spec(self, source: str) -> Dict[str, Any]:
        """Loads an OpenAPI spec from a file."""
        try:
            with open(source, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load OpenAPI spec from {source}: {e}")
            raise e
    
    def _resolve_ref(self, ref_str: str) -> Dict[str, Any]:
        """Resolves a local ref like #/components/schemas/Name"""
        if not ref_str.startswith("#/"):
            return {}
        parts = ref_str[2:].split("/")
        current = self.spec
        for p in parts:
            current = current.get(p, {})
        return current

    def extract_tools(self) -> tuple[List[Dict[str, Any]], Dict[str, dict]]:
        """Converts OpenAPI paths to OpenAI tools format, and returns routing dictionary."""
        tools = []
        routes = {}
        paths = self.spec.get("paths", {})
        
        for path, methods in paths.items():
            for method, details in methods.items():
                if not isinstance(details, dict):
                    continue
                operation_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
                description = details.get("description", f"Executes {method.upper()} on {path}")
                
                # Extract schema
                p_props: Dict[str, Any] = {}
                p_req: List[str] = []
                
                request_body = details.get("requestBody", {})
                if isinstance(request_body, dict) and request_body:
                    try:
                        schema = request_body["content"]["application/json"]["schema"]
                        if isinstance(schema, dict):
                            if "$ref" in schema:
                                schema = self._resolve_ref(str(schema["$ref"]))
                            if isinstance(schema, dict):
                                p_props.update(schema.get("properties", {}))
                                p_req.extend(schema.get("required", []))
                    except KeyError:
                        pass
                
                # Also handle query parameters if any
                for param in details.get("parameters", []):
                    if isinstance(param, dict) and param.get("in") == "query":
                        schema = param.get("schema", {"type": "string"})
                        if isinstance(schema, dict):
                            if "$ref" in schema:
                                schema = self._resolve_ref(str(schema["$ref"]))
                            p_name = str(param.get("name", ""))
                            if p_name:
                                p_props[p_name] = schema
                                if param.get("required"):
                                    p_req.append(p_name)
                        
                tool = {
                    "type": "function",
                    "function": {
                        "name": operation_id,
                        "description": str(description),
                        "parameters": {
                            "type": "object",
                            "properties": p_props,
                            "required": p_req
                        },
                    }
                }
                tools.append(tool)
                routes[operation_id] = {"path": path, "method": method}
                
        return tools, routes
