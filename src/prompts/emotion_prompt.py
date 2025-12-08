from ..core.constants import EMOTION_LIST

SYSTEM_PROMPT = (
    "Classify emotion from the conversation.\n\n"
    "Output format: emotion\n\n"
    "No JSON. Single word only.\n\n"
    f"Emotions: {', '.join(EMOTION_LIST)}"
)


def build_user_prompt(text: str) -> str:
    return f"""
[INPUT]
{text}

[YOUR TEXT OUTPUT: one emotion from the list]
"""

