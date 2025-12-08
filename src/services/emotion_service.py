import time

from ..clients.groq_client_async import AsyncGroqClient
from ..core.config import get_settings
from ..models.enums import EmotionName
from ..models.requests import EmotionRequest
from ..models.responses import EmotionResponse
from ..prompts import emotion_prompt


class EmotionService:
    def __init__(self, client=None):
        # Avoid type-annotated DI params that FastAPI/Pydantic would treat as fields
        self.client = client or AsyncGroqClient()
        self.settings = get_settings()

    async def classify(self, request: EmotionRequest) -> EmotionResponse:
        start = time.perf_counter()

        system_prompt = emotion_prompt.SYSTEM_PROMPT
        user_prompt = emotion_prompt.build_user_prompt(request.input)

        content = await self.client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=self.settings.MAX_TOKENS_EMOTION,
        )

        label = (content or "idle").strip() or "idle"
        latency = (time.perf_counter() - start) * 1000

        # Best-effort enum mapping; fall back to IDLE if unknown.
        try:
            emotion_enum = EmotionName(label)
        except ValueError:
            emotion_enum = EmotionName.IDLE

        return EmotionResponse(emotion_name=emotion_enum, latency_ms=latency)

