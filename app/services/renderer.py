"""Renderer service for histogram visualization."""

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult
from app.styles.elegant_curves import ElegantCurvesStyle
from app.styles.neon_glow import NeonGlowStyle

# Registry of available styles
STYLE_REGISTRY: dict[str, type[BaseStyle]] = {
    "elegant_curves": ElegantCurvesStyle,
    "neon_glow": NeonGlowStyle,
}


def get_available_styles() -> list[str]:
    """Get list of available style names."""
    return list(STYLE_REGISTRY.keys())


def render_histogram(
    data: HistogramData,
    style: str = "elegant_curves",
    width: int = 1200,
    smoothing: float = 0.7,
) -> RenderResult:
    """
    Render histogram data using the specified style.

    Args:
        data: Histogram data to visualize
        style: Style preset name
        width: Output width in pixels
        smoothing: Curve smoothing factor 0.0-1.0

    Returns:
        RenderResult containing PNG bytes and dimensions

    Raises:
        ValueError: If style is not recognized
    """
    if style not in STYLE_REGISTRY:
        raise ValueError(f"Unknown style: {style}. Available: {list(STYLE_REGISTRY.keys())}")

    style_class = STYLE_REGISTRY[style]
    renderer = style_class(width=width, smoothing=smoothing)

    return renderer.render(data)
