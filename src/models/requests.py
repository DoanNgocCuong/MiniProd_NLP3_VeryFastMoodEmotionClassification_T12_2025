from pydantic import BaseModel, Field


class EmotionRequest(BaseModel):
    user_last_message: str = Field(..., description="Last message from user/child")
    pika_response: str = Field(..., description="Robot's response to classify")


class CelebrateRequest(BaseModel):
    user_last_message: str
    pika_response: str


class CombinedRequest(BaseModel):
    user_last_message: str
    pika_response: str

