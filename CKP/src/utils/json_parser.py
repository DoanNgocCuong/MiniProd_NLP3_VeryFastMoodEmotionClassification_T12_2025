import json
from typing import Any, Optional


def safe_json_loads(content: str) -> Optional[Any]:
    """Safely parse JSON string, returning None on failure."""
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None

