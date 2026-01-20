"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.v1 import histogram
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Transform images into artistic RGB histogram visualizations.",
)

app.include_router(histogram.router, prefix="/api/v1", tags=["histogram"])


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}
