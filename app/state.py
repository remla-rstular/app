from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.models.configuration import AppConfiguration


@dataclass
class AppState:
    config: AppConfiguration
    db: Engine
    auth_token: str


app_state: AppState | None = None


def get_app_state() -> AppState:
    if app_state is None:
        raise RuntimeError("App state not initialized")
    return app_state


async def init_app_state() -> AppState:
    global app_state

    config = AppConfiguration()

    with open(config.auth_token_file, "r") as f:
        auth_token = f.read().strip()

    connect_args = {"check_same_thread": False}
    engine = create_engine(f"sqlite:///{config.sqlite_db_path}", connect_args=connect_args)
    SQLModel.metadata.create_all(engine)

    app_state = AppState(config=config, db=engine, auth_token=auth_token)
    return app_state


def get_session():
    with Session(get_app_state().db.engine) as session:
        yield session


AppStateDependency = Annotated[AppState, Depends(get_app_state)]
SessionDependency = Annotated[Session, Depends(get_session)]
