"""FastAPI application entry point."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import histogram
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Transform images into artistic RGB histogram visualizations.",
)

app.include_router(histogram.router, prefix="/api/v1", tags=["histogram"])

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """Serve the web UI."""
    return FileResponse(static_dir / "index.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.version}
