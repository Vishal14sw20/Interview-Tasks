import json
from datetime import datetime


def create_event_structure(event_uuid, event_name, created_at):
    return {
        "event_uuid": event_uuid,
        "event_name": event_name,
        "created_at": created_at,
        "created_datetime": datetime.fromtimestamp(created_at).isoformat(),
        "event_type": event_name.split(':')[0],
        "event_subtype": event_name.split(':')[1] if ':' in event_name else None
    }


if __name__ == "__main__":
    event = create_event_structure("123", "account:created", 1633029200)
    print(json.dumps(event, indent=2))
