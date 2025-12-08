import time

from ..clients.groq_client_async import AsyncGroqClient
from ..core.config import get_settings
from ..models.enums import CelebrateDecision
from ..models.requests import CelebrateRequest
from ..models.responses import CelebrateResponse
from ..prompts import celebrate_prompt


class CelebrateService:
    def __init__(self, client=None):
        # Avoid type-annotated DI params that FastAPI/Pydantic would treat as fields
        self.client = client or AsyncGroqClient()
        self.settings = get_settings()

    async def classify(self, request: CelebrateRequest) -> CelebrateResponse:
        start = time.perf_counter()

        system_prompt = celebrate_prompt.SYSTEM_PROMPT
        user_prompt = celebrate_prompt.build_user_prompt(request.input)

        content = await self.client.complete(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=self.settings.MAX_TOKENS_CELEBRATE,
        )

        decision = (content or "no").strip().lower() or "no"
        latency = (time.perf_counter() - start) * 1000

        try:
            decision_enum = CelebrateDecision(decision)
        except ValueError:
            decision_enum = CelebrateDecision.NO

        return CelebrateResponse(celebrate=decision_enum, latency_ms=latency)

