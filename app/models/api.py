from typing import TypedDict

from pydantic import BaseModel


class SentimentRequest(BaseModel):
    review: str


class SentimentResponse(BaseModel):
    is_positive: bool


class SentimentCorrectionRequest(BaseModel):
    review: str
    correct_sentiment: bool


class StatusResponse(BaseModel):
    success: bool


class VersionResponse(TypedDict):
    app_version: str
    lib_version: str
    model_version: str | None
    model_service_version: str | None
