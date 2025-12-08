from ..core.constants import EMOTION_LIST

SYSTEM_PROMPT = f"""You are an ultra-fast API that detects the emotion in a robot's response.
- Analyze the robot's `pika_response` within the `user_last_message` context.
- Pick the single most fitting emotion from the list.
- Respond ONLY with the emotion name in plain text (no JSON, no quotes).

EMOTION LIST:
{', '.join(f"'{e}'" for e in EMOTION_LIST)}
"""


def build_user_prompt(user_last_message: str, pika_response: str) -> str:
    return f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR TEXT OUTPUT: one emotion from the list]
"""

