from fastapi import APIRouter, Depends

from ..models.requests import CelebrateRequest, CombinedRequest, EmotionRequest
from ..models.responses import CelebrateResponse, CombinedResponse, EmotionResponse
from ..services.celebrate_service import CelebrateService
from ..services.combined_service import CombinedService
from ..services.emotion_service import EmotionService

router = APIRouter(prefix="/api/v1", tags=["Classification"])


@router.post("/emotion", response_model=EmotionResponse)
async def classify_emotion(
    request: EmotionRequest,
    service: EmotionService = Depends(),
) -> EmotionResponse:
    return await service.classify(request)


@router.post("/celebrate", response_model=CelebrateResponse)
async def detect_celebrate(
    request: CelebrateRequest,
    service: CelebrateService = Depends(),
) -> CelebrateResponse:
    return await service.classify(request)


@router.post("/classify", response_model=CombinedResponse)
async def classify_combined(
    request: CombinedRequest,
    service: CombinedService = Depends(),
) -> CombinedResponse:
    return await service.classify_parallel(request)

