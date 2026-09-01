import logging

from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.app_context import AppContext
from controller.storage_controller import router as storage_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    context = AppContext()
    await context.connect_all()
    app.state.context = context  # disponible para toda la app vía request.app.state.context
    yield
    await context.disconnect_all()

app = FastAPI(title="IoT Ingestor", lifespan=lifespan)
app.include_router(storage_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
