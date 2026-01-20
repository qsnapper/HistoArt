"""Application configuration."""

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
    available_styles: set[str] = {"elegant_curves", "neon_glow", "watercolor"}
    default_style: str = "elegant_curves"

    # Rendering defaults
    default_smoothing: float = 0.7


settings = Settings()
