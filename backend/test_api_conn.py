
import asyncio
import os
import sys
import json
from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry

SPEC_PATH = os.path.join(os.path.dirname(__file__), "tools", "openapi.json")

async def test_api_connection():
    print("Testing API connection...")
    loader = OpenAPILoader(SPEC_PATH)
    tools, routes = loader.extract_tools()
    registry = DynamicToolRegistry(
        base_url=settings.CAMPAIGNX_BASE_URL,
        api_key=settings.CAMPAIGNX_API_KEY,
    )
    for tool in tools:
        op_id = tool["function"]["name"]
        route = routes[op_id]
        registry.register_tool(op_id, route["path"], route["method"])
    
    print(f"Base URL: {settings.CAMPAIGNX_BASE_URL}")
    print(f"API Key: {settings.CAMPAIGNX_API_KEY[:5]}...{settings.CAMPAIGNX_API_KEY[-5:]}")
    
    try:
        # Try to get customer cohort
        print("\nAttempting to fetch customer cohort...")
        cohort = await registry.execute(
            "get_customer_cohort_api_v1_get_customer_cohort_get",
            {}
        )
        print("Cohort Response Received!")
        print(f"Count: {cohort.get('total_count')}")
        print(f"Message: {cohort.get('message')}")
        
        # Check for any existing campaigns in the response (though unlikley)
        # Some APIs might return a list of campaigns if you call get_report without an ID, 
        # but the spec says campaign_id is required.
        
    except Exception as e:
        print(f"API Call failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_connection())
