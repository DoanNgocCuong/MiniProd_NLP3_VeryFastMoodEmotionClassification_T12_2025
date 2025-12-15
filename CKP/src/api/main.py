from fastapi import FastAPI

from .routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Emotion Classification Service", version="1.0.0")
    app.include_router(api_router)
    return app


app = create_app()

