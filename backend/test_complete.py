import asyncio
import os
import sys

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.campaign_brief_agent import CampaignBriefAgent
from config import settings

async def main():
    print(f"Current GEMINI_API_KEY: {settings.GEMINI_API_KEY[:5]}...{settings.GEMINI_API_KEY[-5:]}" if settings.GEMINI_API_KEY else "No Key")
    
    print("Testing CampaignBriefAgent...")
    brief_agent = CampaignBriefAgent(model="gemini-2.0-flash")
    
    brief_text = "Run an email campaign for a new shopping credit card targeting urban millennials. Optimize for click rate."
    
    try:
        # We wrapped this in a 30s timeout previously. Let's see if it works.
        result = await asyncio.wait_for(brief_agent.run(brief_text), timeout=35.0)
        print("Success!")
        print(result)
    except Exception as e:
        print(f"Test failed with exception: {type(e).__name__} - {e}")

if __name__ == "__main__":
    asyncio.run(main())
