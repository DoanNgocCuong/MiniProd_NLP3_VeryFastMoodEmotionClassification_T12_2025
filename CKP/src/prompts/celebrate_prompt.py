SYSTEM_PROMPT = """You are an ultra-fast API, a binary classifier for a robot's celebration action.
- `celebrate` is "yes" ONLY IF the provided text confirms the user correctly answered a factual, objective question.
- In ALL other cases (opinions, ideas, feelings, wrong answers), `celebrate` is "no".
- Respond ONLY with yes or no in plain text (no JSON, no quotes).
"""


def build_user_prompt(text: str) -> str:
    return f"""
{text}
"""


