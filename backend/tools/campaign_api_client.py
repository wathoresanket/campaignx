import httpx

class CampaignAPIClient:
    """Wrapper for generic campaign API communications if needed. 
    ExecutionAgent mostly handles dynamic routing, but this can be used for static endpoints."""
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url)
        
    async def get_health(self):
        try:
            resp = await self.client.get("/health")
            return resp.status_code == 200
        except:
            return False
