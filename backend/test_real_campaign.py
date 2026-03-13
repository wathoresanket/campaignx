
import asyncio
import os
import sys
import json
from datetime import datetime, timedelta

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from models import Campaign, Segment, EmailVariant, CampaignRun
from config import settings
from tools.openapi_loader import OpenAPILoader
from tools.dynamic_tool_registry import DynamicToolRegistry
from engines.brief_processor import BriefProcessor
from engines.segment_engine import SegmentEngine
from engines.content_engine import ContentEngine
from engines.execution_engine import ExecutionEngine
from engines.analytics_engine import AnalyticsEngine
from engines.insight_engine import InsightEngine

SPEC_PATH = os.path.join(os.path.dirname(__file__), "tools", "openapi.json")

async def run_real_campaign():
    print("🚀 Starting Real API Campaign Test...")
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

        # 3. Plan Phase
        brief_text = "Run a high-urgency email campaign for our premium travel credit card targeting active travelers."
        print(f"\n📝 Brief: {brief_text}")
        
        brief_agent = CampaignBriefAgent()
        parsed_brief = await brief_agent.run(brief_text)
        print("✅ Parsed brief.")

        segmentation_agent = SegmentationAgent()
        segments = await segmentation_agent.run(parsed_brief, cohort_data=cohort_data)
        print(f"✅ Created {len(segments)} segments.")

        # For the test, we'll just use the first 2 segments and a few customers per segment to avoid hitting rate limits or body size limits
        active_segments = segments[:2]
        print(f"🔹 Using first {len(active_segments)} segments for test.")

        content_agent = ContentAgent()
        # Mocking strategy for speed in test
        strategies = []
        for s in active_segments:
            strategies.append({"segment_name": s["name"], "variants": ["A", "B"], "best_send_time": "10:00:00"})
            
        variants = await content_agent.run(parsed_brief, strategies)
        print("✅ Generated email variants.")

        # 4. Save to DB for tracking (Minimal)
        campaign = Campaign(brief=brief_text, product="Travel Card", status="running")
        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        exec_plan = {}
        segments_info = []
        
        for idx, s_data in enumerate(active_segments):
            seg = Segment(campaign_id=campaign.id, name=s_data["name"], customer_ids=json.dumps(s_data["customer_ids"]), customer_count=len(s_data["customer_ids"]))
            db.add(seg)
            db.commit()
            db.refresh(seg)
            
            # Map variants
            exec_plan[str(seg.id)] = []
            s_variants = variants.get(seg.name, [])
            for v_data in s_variants:
                v = EmailVariant(segment_id=seg.id, variant_label=v_data["label"], subject=v_data["subject"], body=v_data["body"])
                db.add(v)
                exec_plan[str(seg.id)].append({"label": v.variant_label, "subject": v.subject, "body": v.body})
            
            db.commit()
            
            segments_info.append({
                "id": seg.id,
                "segment_id": str(seg.id),
                "name": seg.name,
                "customer_ids": json.dumps(s_data["customer_ids"][:10]), # Use only 10 customers per segment for test
                "customer_count": 10
            })

        # 5. EXECUTION: Send Campaign
        print("\n📤 Dispatching real campaign emails via API...")
        # We need a future send time
        future_time = (datetime.now() + timedelta(days=1)).strftime("%d:%m:%y 12:00:00")
        
        # We need to set the send_time in the execution plan or mock the ExecutionAgent to use it
        execution_agent = ExecutionAgent()
        # ExecutionAgent internally uses registry.execute("send_campaign_api_v1_send_campaign_post", ...)
        # We'll pass the future_time via a patch or just let it use its default (which we should check)
        
        with patch('engines.execution_engine.datetime') as mock_date:
            # We want current time + 1 day
            mock_date.now.return_value = datetime.now()
            mock_date.utcnow.return_value = datetime.utcnow()
            
            exec_result = await execution_agent.run(exec_plan, segments_with_ids=segments_info)

        sent_campaigns = exec_result.get("sent_campaigns", [])
        print(f"✅ Dispatched {len(sent_campaigns)} campaigns.")
        for sc in sent_campaigns:
            print(f"  - Segment: {sc['segment_name']}, ID: {sc['api_campaign_id']}")

        # 6. ANALYTICS: Fetch Report
        print("\n📊 Fetching reports for dispatched campaigns...")
        analytics_agent = AnalyticsAgent()
        metrics = await analytics_agent.run(sent_campaigns)
        
        print("\nSummary Metrics:")
        for m in metrics:
            print(f"  Segment: {m['segment_name']}, Open: {m['open_rate']:.2%}, Click: {m['click_rate']:.2%}")

        # 7. INSIGHTS
        print("\n💡 Generating marketing insights...")
        insight_agent = InsightAgent()
        insights = await insight_agent.run(metrics)
        
        print("\nFinal Insights:")
        for i in insights:
            print("-" * 30)
            print(f"Segment: {i['segment_name']}")
            print(f"Insight: {i['key_insight']}")
            print(f"Rec: {i['recommendation']}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    from unittest.mock import patch
    asyncio.run(run_real_campaign())
