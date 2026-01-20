"""Pydantic schemas for histogram API."""

from pydantic import BaseModel, Field


class HistogramMetadata(BaseModel):
    """Metadata about the generated histogram."""

    width: int = Field(..., description="Output image width in pixels")
    height: int = Field(..., description="Output image height in pixels")
    dominant_colors: list[str] = Field(
        ..., description="Top 5 dominant colors from source image as hex codes"
    )
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")


class HistogramResponse(BaseModel):
    """Response containing the generated histogram."""

    image: str = Field(..., description="Base64 encoded PNG image")
    metadata: HistogramMetadata
