import asyncio
from engines.base_engine import BaseEngine

async def test():
    print("Initializing agent...")
    agent = BaseEngine()
    print("Calling API...")
    try:
        res = await asyncio.wait_for(agent._complete_json("Return {\"status\": \"ok\"}"), timeout=10.0)
        print("Response:", res)
    except asyncio.TimeoutError:
        print("TIMEOUT: API hung forever")
    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    asyncio.run(test())
