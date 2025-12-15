from pydantic import BaseModel

from .enums import CelebrateDecision, EmotionName


class EmotionResponse(BaseModel):
    emotion_name: EmotionName
    latency_ms: float


class CelebrateResponse(BaseModel):
    celebrate: CelebrateDecision
    latency_ms: float


class CombinedResponse(BaseModel):
    emotion_name: EmotionName
    celebrate: CelebrateDecision
    total_latency_ms: float

