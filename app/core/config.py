"""Application configuration."""

import os

from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings."""

    app_name: str = "Artistic RGB Histogram API"
    version: str = "0.1.0"

    # Image constraints
    max_file_size_mb: int = 50
    max_output_width: int = 4096
    default_output_width: int = 1200

    # Supported formats
    supported_formats: set[str] = {"image/jpeg", "image/png", "image/webp", "image/tiff"}

    # Available styles
    available_styles: set[str] = {"elegant_curves", "minimal", "neon_glow", "original", "tron", "watercolor"}
    default_style: str = "elegant_curves"

    # Rendering defaults
    default_smoothing: float = 0.7
    default_aspect_ratio: float = 1.618  # Golden ratio

    # Available aspect ratios (value: label)
    available_aspect_ratios: dict[float, str] = {
        1.618: "Golden Ratio",
        1.778: "16:9 (Widescreen)",
        1.333: "4:3 (Classic)",
        1.0: "1:1 (Square)",
        1.5: "3:2 (Photo)",
        2.333: "21:9 (Ultrawide)",
    }

    # OpenRouter API settings (for LLM-enhanced watercolor style)
    openrouter_api_key: str | None = os.environ.get("OPENROUTER_API_KEY")
    openrouter_image_model: str = os.environ.get(
        "OPENROUTER_IMAGE_MODEL", "google/gemini-2.5-flash-image"
    )


settings = Settings()
