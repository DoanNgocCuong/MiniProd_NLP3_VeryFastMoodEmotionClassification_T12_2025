SYSTEM_PROMPT = """You are an ultra-fast API, a binary classifier for a robot's celebration action.
- `celebrate` is "yes" ONLY IF the `pika_response` confirms the user correctly answered a factual, objective question.
- In ALL other cases (opinions, ideas, feelings, wrong answers), `celebrate` is "no".
- Respond ONLY with yes or no in plain text (no JSON, no quotes).
"""


def build_user_prompt(user_last_message: str, pika_response: str) -> str:
    return f"""
[CONTEXT]
user_last_message: "{user_last_message}"
pika_response: "{pika_response}"

[YOUR TEXT OUTPUT: yes or no]
"""

