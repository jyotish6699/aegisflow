from fastapi import HTTPException

from constants.event_types import EventTypes


# =====================================================
# Payload Contracts
# =====================================================

PAYLOAD_CONTRACTS = {

    EventTypes.SESSION_STARTED: set(),

    EventTypes.SESSION_COMPLETED: set(),

    EventTypes.WORKSPACE_PROJECT_UPDATED: {
        "project_name"
    },

    EventTypes.WORKSPACE_TASK_UPDATED: {
        "task_name"
    },

    EventTypes.WORKSPACE_NOTE_UPDATED: {
        "notes"
    },

    EventTypes.SESSION_SUMMARY_UPDATED: {
        "summary"
    },

    EventTypes.SESSION_NEXT_STEP_UPDATED: {
        "next_step"
    }

}


# =====================================================
# Event Validator
# =====================================================

def validate_event(event: dict):

    validate_event_type(event["event_type"])

    validate_payload(
        event["event_type"],
        event["payload"]
    )


# =====================================================
# Event Type Validation
# =====================================================

def validate_event_type(event_type: str):

    if event_type not in EventTypes.ALL:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported event type: {event_type}"
        )


# =====================================================
# Payload Validation
# =====================================================

def validate_payload(
    event_type: str,
    payload: dict
):

    required_fields = PAYLOAD_CONTRACTS[event_type]

    payload_fields = set(payload.keys())

    if payload_fields != required_fields:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid payload for '{event_type}'. "
                f"Expected: {sorted(required_fields)}, "
                f"Received: {sorted(payload_fields)}"
            )
        )