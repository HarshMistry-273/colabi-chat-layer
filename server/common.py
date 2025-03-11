from datetime import datetime
import json
import re

def get_datetime_info():
    now = datetime.now()
    
    return {
        "date": now.strftime("%Y-%m-%d"),  # e.g., "2025-03-10"
        "time": now.strftime("%H:%M:%S"),  # e.g., "15:45:30"
        "day": now.strftime("%A")          # e.g., "Monday"
    }

def extract_json(bot_response: str):
    match = re.search(r"```json\n(.*?)\n```", bot_response, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str), True # Convert to a Python dictionary
        except json.JSONDecodeError:
            return "", False  # Return False if the extracted text is not valid JSON
    return "", False  # Return False if no JSON is found