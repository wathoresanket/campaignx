import asyncio
import json
import logging
import sys
import os

sys.path.append(os.getcwd())

from engines.brief_processor import BriefProcessor

logging.basicConfig(level=logging.INFO)

async def test_brief_extraction():
    processor = BriefProcessor()
    
    brief_text = "“Run email campaign for launching XDeposit, a flagship term deposit product from SuperBFSI, that gives 1 percentage point higher returns than its competitors. Announce an additional 0.25 percentage point higher returns for female senior citizens. Optimise for open rate and click rate. Don’t skip emails to customers marked ‘inactive’. Include the call to action: https://superbfsi.com/xdeposit/explore/.”"
    
    print(f"Testing brief: {brief_text}")
    print("-" * 50)
    
    result = await processor.run(brief_text)
    
    print("\nParsed Result:")
    print(json.dumps(result, indent=2))
    
    target_segments = result.get("target_segments", [])
    print(f"\nExtracted Target Segments: {target_segments}")
    
    assert any("female" in s.lower() and "senior" in s.lower() for s in target_segments), "Should contain female senior citizens"
    assert any("inactive" in s.lower() for s in target_segments), "Should contain inactive customers"
    
    print("\n✅ BriefProcessor extraction verified!")

if __name__ == "__main__":
    asyncio.run(test_brief_extraction())
