import asyncio
import time

from ..models.requests import CombinedRequest
from ..models.responses import CombinedResponse
from .celebrate_service import CelebrateService
from .emotion_service import EmotionService


class CombinedService:
    def __init__(
        self,
        emotion_service=None,
        celebrate_service=None,
    ):
        # Avoid type-annotated DI params that FastAPI/Pydantic would try to treat as fields
        self.emotion_service = emotion_service or EmotionService()
        self.celebrate_service = celebrate_service or CelebrateService()

    async def classify_parallel(self, request: CombinedRequest) -> CombinedResponse:
        start = time.perf_counter()

        emotion_task = self.emotion_service.classify(request)
        celebrate_task = self.celebrate_service.classify(request)

        emotion_result, celebrate_result = await asyncio.gather(
            emotion_task, celebrate_task
        )

        total_latency = (time.perf_counter() - start) * 1000

        return CombinedResponse(
            emotion_name=emotion_result.emotion_name,
            celebrate=celebrate_result.celebrate,
            total_latency_ms=total_latency,
        )

