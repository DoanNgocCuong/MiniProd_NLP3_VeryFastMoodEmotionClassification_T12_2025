from pydantic import BaseModel, Field


class EmotionRequest(BaseModel):
    input: str = Field(..., description="Text to classify the robot's emotion from")


class CelebrateRequest(BaseModel):
    input: str


class CombinedRequest(BaseModel):
    input: str

