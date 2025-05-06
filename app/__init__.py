import os
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
    await init_app_state()
    yield


app = FastAPI(
    title="Restaurant review sentiment analysis",
    description="A simple API to predict the sentiment of restaurant reviews using a pre-trained model.",
    version=os.getenv("SERVICE_VERSION", "N/A"),
    lifespan=lifespan,
)


@app.get("/api/version")
async def get_version(app_state: AppStateDependency) -> VersionResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            urljoin(app_state.config.model_service_url, "/version/app"),
            headers={"Authorization": f"Bearer {app_state.auth_token}"},
        ) as model_service_response, session.get(
            urljoin(app_state.config.model_service_url, "/version/model"),
            headers={"Authorization": f"Bearer {app_state.auth_token}"},
        ) as model_response:
            model_version: dict[str, Any] = await model_response.json()
            model_service_version: dict[str, Any] = await model_service_response.json()
            return VersionResponse(
                app_version=os.getenv("SERVICE_VERSION", "N/A"),
                lib_version=f"v{version}",
                model_version=model_version.get("version"),
                model_service_version=model_service_version.get("version"),
            )


@app.post("/api/sentiment")
async def predict_sentiment(
    app_state: AppStateDependency, payload: SentimentRequest
) -> ModelServicePredictResponse:
    async with aiohttp.ClientSession() as session:
        req = ModelServicePredictRequest(review=payload.review)
        async with session.post(
            urljoin(app_state.config.model_service_url, "/predict"),
            json=req.model_dump(),
            headers={"Authorization": f"Bearer {app_state.auth_token}"},
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
