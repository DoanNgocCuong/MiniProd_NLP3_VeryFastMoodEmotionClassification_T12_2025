from ..services.celebrate_service import CelebrateService
from ..services.combined_service import CombinedService
from ..services.emotion_service import EmotionService


def get_emotion_service() -> EmotionService:
    return EmotionService()


def get_celebrate_service() -> CelebrateService:
    return CelebrateService()


def get_combined_service() -> CombinedService:
    return CombinedService()

