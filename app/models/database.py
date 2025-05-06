from sqlmodel import SQLModel, Field


class Correction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    review: str
    correct_sentiment: bool
