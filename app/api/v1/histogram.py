"""Histogram API endpoint."""

import base64
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.histogram import HistogramMetadata, HistogramResponse
from app.services.histogram import calculate_histogram
from app.services.renderer import render_histogram

router = APIRouter()


@router.post("/histogram", response_model=HistogramResponse)
async def create_histogram(
    image: UploadFile = File(..., description="Source image file (JPEG, PNG, WebP, TIFF)"),
    style: str = Form(default=settings.default_style, description="Visual style preset"),
    width: int = Form(default=settings.default_output_width, description="Output width in pixels"),
    smoothing: float = Form(default=settings.default_smoothing, description="Curve smoothing 0.0-1.0"),
    aspect_ratio: float = Form(default=settings.default_aspect_ratio, description="Output aspect ratio (width/height)"),
):
    """
    Generate an artistic RGB histogram visualization from an uploaded image.

    Returns a base64 encoded PNG image along with metadata about the visualization.
    """
    start_time = time.time()

    # Validate content type
    if image.content_type not in settings.supported_formats:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_IMAGE",
                "message": f"Unsupported image format: {image.content_type}. "
                f"Supported formats: {', '.join(settings.supported_formats)}",
            },
        )

    # Validate style
    if style not in settings.available_styles:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STYLE",
                "message": f"Unknown style: {style}. "
                f"Available styles: {', '.join(settings.available_styles)}",
            },
        )

    # Validate width
    if width < 100 or width > settings.max_output_width:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_WIDTH",
                "message": f"Width must be between 100 and {settings.max_output_width} pixels.",
            },
        )

    # Validate smoothing
    if smoothing < 0.0 or smoothing > 1.0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_SMOOTHING",
                "message": "Smoothing must be between 0.0 and 1.0.",
            },
        )

    # Validate aspect_ratio
    if aspect_ratio not in settings.available_aspect_ratios:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_ASPECT_RATIO",
                "message": f"Unknown aspect ratio: {aspect_ratio}. "
                f"Available: {list(settings.available_aspect_ratios.keys())}",
            },
        )

    # Read image bytes
    image_bytes = await image.read()

    # Check file size
    max_size_bytes = settings.max_file_size_mb * 1024 * 1024
    if len(image_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "IMAGE_TOO_LARGE",
                "message": f"Image exceeds maximum size of {settings.max_file_size_mb}MB.",
            },
        )

    try:
        # Calculate histogram
        histogram_data = calculate_histogram(image_bytes)

        # Render visualization
        result = render_histogram(
            data=histogram_data,
            style=style,
            width=width,
            smoothing=smoothing,
            aspect_ratio=aspect_ratio,
        )

        # Encode to base64
        image_base64 = base64.b64encode(result.image_bytes).decode("utf-8")

        # Calculate processing time
        processing_time_ms = int((time.time() - start_time) * 1000)

        return HistogramResponse(
            image=image_base64,
            metadata=HistogramMetadata(
                width=result.width,
                height=result.height,
                dominant_colors=histogram_data.dominant_colors,
                processing_time_ms=processing_time_ms,
            ),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "PROCESSING_ERROR",
                "message": f"Error processing image: {str(e)}",
            },
        )
