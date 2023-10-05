from typing import Dict


async def generate_event(previous_data: Dict, current_data: Dict) -> Dict:

    events = {}

    for key, value in previous_data.items():
        if current_data[key] != value:
            events[key] = value

    return events

