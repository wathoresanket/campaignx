import asyncio
import json
import logging
import sys
import os

sys.path.append(os.getcwd())

from engines.content_engine import ContentEngine

logging.basicConfig(level=logging.INFO)

async def test_content_leakage():
    engine = ContentEngine()
    
    parsed_brief = {
        "product": "PDeposit Term Deposit",
        "global_benefits": ["9 percentage point higher returns than competitors"],
        "conditional_benefits": [
             "0.85 percentage point higher returns for male young citizens"
        ],
        "tone": "professional",
        "cta_url": "https://superbfsi.com/xdeposit/explore/"
    }
    
    # Segment that should NOT get the 0.85%
    strategy_senior = {
        "segment_name": "senior citizens",
        "description": "Retired individuals looking for secure growth."
    }
    
    # Segment that SHOULD get the 0.85% (matches both 'male' and 'young')
    strategy_young_male = {
        "segment_name": "male young citizens",
        "description": "Young men starting their investment journey."
    }

    print(f"Testing Benefit Leakage...")
    print("-" * 50)
    
    # 1. Test Senior Citizen (Ineligible for 0.85%)
    print("\n[Test 1] Generating for 'senior citizens'...")
    res_senior = await engine._generate_for_segment(parsed_brief, strategy_senior, "")
    body_senior = res_senior["variants"][0]["body"]
    print(f"Senior Body Snippet: {body_senior[:200]}...")
    
    if "0.85" in body_senior:
        print("❌ FAILED: Senior citizen email contains '0.85'!")
    else:
        print("✅ SUCCESS: Senior citizen email does not contain unauthorized '0.85'.")

    # 2. Test Young Male (Eligible for 0.85%)
    print("\n[Test 2] Generating for 'male young citizens'...")
    res_young = await engine._generate_for_segment(parsed_brief, strategy_young_male, "")
    body_young = res_young["variants"][0]["body"]
    print(f"Young Male Body Snippet: {body_young[:200]}...")
    
    if "0.85" in body_young:
        print("✅ SUCCESS: Young male email correctly contains '0.85'.")
    else:
        print("❌ FAILED: Young male email is missing their specific benefit '0.85'.")

if __name__ == "__main__":
    asyncio.run(test_content_leakage())
