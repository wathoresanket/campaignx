import json
from sqlalchemy.orm import Session
from models import AgentLog

def log_agent_action(
    db: Session,
    agent_name: str,
    campaign_id: int,
    input_data: dict,
    output_data: dict,
    reasoning_summary: str,
    api_calls_executed: dict = None,
    status: str = "completed",
    action_description: str = None,
):
    """
    Logs an agent action to the database.
    status: 'running', 'completed', or 'error'
    action_description: Short human-readable text (e.g., 'Parsing campaign brief')
    """
    log_entry = AgentLog(
        agent_name=agent_name,
        campaign_id=campaign_id,
        input_data=json.dumps(input_data) if isinstance(input_data, dict) else str(input_data),
        output_data=json.dumps(output_data) if isinstance(output_data, dict) else str(output_data),
        reasoning_summary=reasoning_summary,
        api_calls_executed=json.dumps(api_calls_executed) if api_calls_executed else "{}",
        status=status,
        action_description=action_description or reasoning_summary,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
