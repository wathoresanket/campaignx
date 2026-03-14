import asyncio
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from pprint import pprint
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "backend", ".env"))

# Ensure backend is in path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

from backend.database import SessionLocal
from backend.models import Campaign, Segment, EmailVariant
from backend.engines.brief_processor import BriefProcessor
from backend.engines.segment_engine import SegmentEngine
from backend.engines.strategy_engine import StrategyEngine
from backend.engines.content_engine import ContentEngine
from backend.tools.dynamic_tool_registry import DynamicToolRegistry
from backend.tools.openapi_loader import OpenAPILoader
from backend.config import settings

SPEC_PATH = os.path.join(os.path.dirname(__file__), "backend", "tools", "openapi.json")

async def test_generation_constraints():
    print("🚀 Starting Segment & Tailored Content Generation Test...")
    db = SessionLocal()
    
    try:
        # 1. API Discovery
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
        
        # 2. Fetch REAL cohort
        print("\n📥 Fetching real customer cohort from API...")
        cohort_response = await registry.execute("get_customer_cohort_api_v1_get_customer_cohort_get", {})
        cohort_data = cohort_response.get("data", [])
        print(f"✅ Fetched {len(cohort_data)} customers.")

        # 3. Complex Brief with specific numbers and conditional benefits
        brief_text = """
        Launch a campaign for our new 'SuperSaver Fixed Deposit'.
        The interest rate is exactly 6.50% p.a. for standard accounts.
        IMPORTANT CONDITIONS:
        - Senior Citizens (60+ years old) get an extra 0.50% (total 7.00% p.a.).
        - Salaried Professionals get a guaranteed ₹1,000 Amazon Voucher upon booking an FD of ₹50,000 or more.
        - The campaign tone should be secure and trustworthy.
        Optimized for click_rate. CTA is https://superbank.com/fd.
        """
        print(f"\n📝 Test Brief Submitted:\n{brief_text}")
        
        # 4. Processing
        print("\n⏳ Running Brief Processing...")
        brief_processor = BriefProcessor()
        for attempt in range(5):
            try:
                parsed_brief = await brief_processor.run(brief_text)
                break
            except Exception as e:
                if attempt == 4: raise e
                print(f"Rate limited... Retrying in {5 * (attempt+1)}s")
                await asyncio.sleep(5 * (attempt+1))
                
        print("\n✅ Parsed Brief Results:")
        pprint(parsed_brief)
        
        print("\n🧠 Running Segmentation...")
        segment_engine = SegmentEngine()
        segments = await segment_engine.run(parsed_brief, cohort_data=cohort_data)
        
        print(f"\n✅ Created {len(segments)} segments. Details:")
        for s in segments:
            print(f"- {s.get('name', 'Unknown')} ({len(s.get('customer_ids', []))} customers): {s.get('description', 'No description')}")
            
        print("\n⏳ Running Strategy Generation...")
        strategy_engine = StrategyEngine()
        strategies = await strategy_engine.run(segments)
        
        print("\n✍️ Running Content Generation (Focusing on Constraints)...")
        content_engine = ContentEngine()
        variants = await content_engine.run(parsed_brief, strategies)
        
        print("\n" + "="*50)
        print("🔍 GENERATED CONTENT VERIFICATION")
        print("="*50)
        
        for seg_name, seg_variants in variants.items():
            print(f"\n\n🎯 SEGMENT: {seg_name}")
            for v in seg_variants:
                print("-" * 30)
                print(f"[{v['label']}] SUBJECT: {v['subject']}")
                print(f"BODY:\n{v['body']}")
                
                # Check for hallucinations / conditional constraints
                body_lower = v['body'].lower()
                
                # Test logic checks
                print("\n  >> Constraint Checks:")
                if "6.50%" in body_lower or "6.5%" in body_lower:
                    print("  ✅ Base rate (6.50%) correctly included.")
                else:
                    print("  ❌ WARNING: Base rate (6.50%) missing.")
                    
                if "7.00%" in body_lower or "7%" in body_lower or "0.50%" in body_lower:
                    if "senior" in seg_name.lower():
                        print("  ✅ Senior Citizen rate correctly included for this segment.")
                    else:
                        print("  ❌ CRITICAL FAILURE: Senior Citizen rate hallucinated into non-senior segment!")
                        
                if "1,000" in body_lower or "amazon" in body_lower:
                    if "professional" in seg_name.lower() or "salaried" in seg_name.lower():
                        print("  ✅ Amazon Voucher correctly included for professionals.")
                    else:
                        print("  ❌ CRITICAL FAILURE: Amazon Voucher hallucinated into non-professional segment!")
                        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_generation_constraints())
