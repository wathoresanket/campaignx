import asyncio
import json
import logging
import sys
import os

# Add parent directory to path since we're running from backend/
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.getcwd())

from engines.segment_engine import SegmentEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_segmentation_logic():
    engine = SegmentEngine()
    
    # Mock cohort data
    cohort_data = [
        {"customer_id": "C001", "Age": 25, "Name": "Alice"},
        {"customer_id": "C002", "Age": 65, "Name": "Bob"},
        {"customer_id": "C003", "Age": 22, "Name": "Charlie"},
    ]
    
    # Mock parsed brief
    parsed_brief = {
        "target_segments": ["young adults"],
        "product": "Savings Account"
    }

    # 1. Test _apply_rules ordering and empty segments
    logger.info("--- Testing _apply_rules logic ---")
    mock_rules = [
        {"name": "Catch All", "catch_all": True},  # Catch-all is first in list!
        {"name": "Senior Citizens", "condition": "c.get('Age', 0) >= 60"},
        {"name": "Teenagers", "condition": "c.get('Age', 0) < 20"}, # Should be empty
    ]
    
    segments = engine._apply_rules(mock_rules, cohort_data)
    
    print("\nResulting Segments:")
    for s in segments:
        print(f"Name: {s['name']}, Count: {s['customer_count']}, IDs: {s['customer_ids']}")

    # Assertions
    names = [s['name'] for s in segments]
    assert names == ["Senior Citizens", "Teenagers", "Catch All"], f"Incorrect order: {names}"
    
    senior = next(s for s in segments if s['name'] == "Senior Citizens")
    assert senior['customer_count'] == 1
    assert senior['customer_ids'] == ["C002"]
    
    teen = next(s for s in segments if s['name'] == "Teenagers")
    assert teen['customer_count'] == 0, "Teenagers should be 0"
    
    catch_all = next(s for s in segments if s['name'] == "Catch All")
    assert catch_all['customer_count'] == 2
    assert set(catch_all['customer_ids']) == {"C001", "C003"}

    logger.info("✅ _apply_rules logic verified!")

    # 2. Test Feedback Injection in prompt
    logger.info("\n--- Testing prompt injection ---")
    feedback = "Exclude anyone named Bob"
    
    # We'll monkeypatch _complete_pydantic to just return the prompt for inspection
    original_complete = engine._complete_pydantic
    captured_prompt = ""
    
    async def mock_complete(prompt, schema):
        nonlocal captured_prompt
        captured_prompt = prompt
        # Return a dummy result that matches the schema structure
        from pydantic import BaseModel
        class DummyRule(BaseModel):
            name: str
            condition: str
            catch_all: bool = False
        class DummyResult(BaseModel):
            segments: list[DummyRule]
        return DummyResult(segments=[DummyRule(name="Test", condition="True")])

    engine._complete_pydantic = mock_complete
    await engine.run(parsed_brief, cohort_data, feedback=feedback)
    
    assert "REJECTION FEEDBACK TO ADDRESS:" in captured_prompt
    assert feedback in captured_prompt
    logger.info("✅ Feedback injection verified!")

if __name__ == "__main__":
    asyncio.run(test_segmentation_logic())
