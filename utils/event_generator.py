from typing import Dict


async def generate_event(previous_data: Dict, current_data: Dict) -> Dict:

    events = {}

    for key, value in current_data.items():
        if previous_data[key] != value:
            events[key] = previous_data[key]

    events.update({'id': current_data.get('id')})

    return events

