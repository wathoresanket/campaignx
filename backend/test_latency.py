import asyncio
import time
from agents.base_agent import BaseAgent

async def test():
    agent = BaseAgent()
    print("Sending request to Groq...")
    start = time.time()
    try:
        res = await agent._complete_json("Return {\"hello\": \"world\"}")
        print(f"Response in {time.time() - start:.2f}s: {res}")
    except Exception as e:
        print(f"Failed in {time.time() - start:.2f}s: {e}")

if __name__ == "__main__":
    asyncio.run(test())
