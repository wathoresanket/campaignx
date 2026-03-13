import json
from sqlalchemy.orm import Session
from models import SystemLog

def log_system_action(
    db: Session,
    module_name: str,
    campaign_id: int,
    input_data: dict,
    output_data: dict,
    logic_summary: str,
    external_calls: dict = None,
    status: str = "completed",
    action_description: str = None,
):
    """
    Logs an internal system action to the database.
    status: 'running', 'completed', or 'error'
    action_description: Short human-readable text (e.g., 'Parsing campaign brief')
    """
    log_entry = SystemLog(
        module_name=module_name,
        campaign_id=campaign_id,
        input_data=json.dumps(input_data) if isinstance(input_data, dict) else str(input_data),
        output_data=json.dumps(output_data) if isinstance(output_data, dict) else str(output_data),
        logic_summary=logic_summary,
        external_calls=json.dumps(external_calls) if external_calls else "{}",
        status=status,
        action_description=action_description or logic_summary,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry
