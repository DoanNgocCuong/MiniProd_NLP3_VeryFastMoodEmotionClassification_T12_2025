from ..core.constants import EMOTION_LIST

SYSTEM_PROMPT = (
    "Classify emotion from the conversation.\n\n"
    "Output format: emotion\n\n"
    "No JSON. Single word only.\n\n"
    "Emotions: happy, calm, excited, playful, no_problem, encouraging, curious, surprised, proud, thats_right, sad, angry, worry, afraid, noisy, thinking"
)


def build_user_prompt(text: str) -> str:
    return f"""
[INPUT]
{text}

[YOUR TEXT OUTPUT: one emotion from the list]
"""

