import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI

from .api.routers import router
from .services.pipeline import ReceiptPipeline
from .core.logger_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

receipt_pipeline = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global receipt_pipeline
    logger.info("Starting Receipt Extraction Service...")

    try:
        receipt_pipeline = ReceiptPipeline()
        logger.info("AI Models initialized successfully!")
    except Exception as e:
        logger.critical(f"Failed to initialize AI models: {e}", exc_info=True)

    yield

    logger.info("Shutting down service...")


app = FastAPI(title="Receipt Extraction Service", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/health")
def health():
    is_ready = receipt_pipeline is not None
    if is_ready:
        logger.debug("Health check passed")
        return {"status": "ok"}
    else:
        logger.warning("Health check failed: models not loaded")
        return {"status": "loading"}
