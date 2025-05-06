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
