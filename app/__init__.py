from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urljoin

import aiohttp
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from lib_version import version
from lib_version.dto import ModelServicePredictRequest, ModelServicePredictResponse

from app.models.api import (
    SentimentCorrectionRequest,
    SentimentRequest,
    SentimentResponse,
    StatusResponse,
    VersionResponse,
)
from app.models.database import Correction
from app.state import AppStateDependency, SessionDependency, init_app_state


@asynccontextmanager
async def lifespan(_: FastAPI):
    app_state = await init_app_state()
    yield


app = FastAPI(
    title="Restaurant review sentiment analysis",
    description="A simple API to predict the sentiment of restaurant reviews using a pre-trained model.",
    version=version,
    lifespan=lifespan,
)


@app.get("/api/version")
async def get_version(app_state: AppStateDependency) -> VersionResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            urljoin(app_state.config.model_service_url, "/version/app")
        ) as app_response, session.get(
            urljoin(app_state.config.model_service_url, "/version/model")
        ) as model_response:
            model_service_version: dict[str, Any] = await model_response.json()
            app_version: dict[str, Any] = await app_response.json()
            return VersionResponse(
                version=f"v{version}",
                model_version=model_service_version.get("version"),
                model_service_version=app_version.get("version"),
            )


@app.post("/api/sentiment")
async def predict_sentiment(
    app_state: AppStateDependency, payload: SentimentRequest
) -> ModelServicePredictResponse:
    async with aiohttp.ClientSession() as session:
        req = ModelServicePredictRequest(review=payload.review)
        async with session.post(
            urljoin(app_state.config.model_service_url, "/predict"), json=req.model_dump()
        ) as response:
            model_response = ModelServicePredictResponse.model_validate_json(await response.json())
            return SentimentResponse(is_positive=model_response.is_positive)


@app.post("/api/correct")
async def correct_sentiment(
    db_session: SessionDependency, payload: SentimentCorrectionRequest
) -> StatusResponse:
    correction = Correction(
        review=payload.review,
        correct_sentiment=payload.correct_sentiment,
    )
    db_session.add(correction)
    db_session.commit()
    return StatusResponse(success=True)


app.mount("/", StaticFiles(directory="app/static", html=True), name="static")
