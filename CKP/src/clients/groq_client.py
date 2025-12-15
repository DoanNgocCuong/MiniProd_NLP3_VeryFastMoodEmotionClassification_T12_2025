from __future__ import annotations

import os
from typing import Optional

from groq import Groq
from groq._exceptions import GroqError as GroqSDKError

from ..core.config import get_settings
from ..core.exceptions import ConfigError, GroqError


class GroqClient:
    """Sync Groq client wrapper for plain-text completions."""

    def __init__(self, client: Optional[Groq] = None):
        settings = get_settings()
        api_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
        if not api_key:
            raise ConfigError("GROQ_API_KEY is not set.")

        self.client = client or Groq(api_key=api_key, timeout=settings.GROQ_TIMEOUT)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.TEMPERATURE
        self.top_p = settings.TOP_P

    def complete(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Return plain-text completion content."""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=max_tokens,
                top_p=self.top_p,
            )
        except GroqSDKError as exc:
            raise GroqError(str(exc)) from exc

        content = completion.choices[0].message.content or ""
        return content.strip()

