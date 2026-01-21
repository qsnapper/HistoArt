"""Base class for histogram visualization styles."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import BytesIO

import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for server use
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d

from app.services.histogram import HistogramData


@dataclass
class RenderResult:
    """Result of rendering a histogram."""

    image_bytes: bytes  # PNG bytes
    width: int
    height: int


class BaseStyle(ABC):
    """Abstract base class for histogram visualization styles."""

    # Color definitions from PRD
    RED_DARK = "#4A0000"  # Deep burgundy
    RED_LIGHT = "#FF3333"  # Vivid scarlet
    GREEN_DARK = "#004A00"  # Forest
    GREEN_LIGHT = "#33FF33"  # Electric lime
    BLUE_DARK = "#00004A"  # Navy
    BLUE_LIGHT = "#3333FF"  # Brilliant azure

    def __init__(self, width: int = 1200, smoothing: float = 0.7, aspect_ratio: float = 1.618):
        """
        Initialize the style renderer.

        Args:
            width: Output width in pixels
            smoothing: Curve smoothing factor 0.0-1.0
            aspect_ratio: Width-to-height ratio for output image
        """
        self.width = width
        self.height = int(width / aspect_ratio)
        self.smoothing = smoothing
        # DPI for matplotlib (100 DPI means width in pixels = figsize * 100)
        self.dpi = 100

    def smooth_histogram(self, hist: np.ndarray) -> np.ndarray:
        """Apply Gaussian smoothing to histogram data."""
        if self.smoothing <= 0:
            return hist
        # sigma scales with smoothing factor (0-1 maps to 0-10 sigma)
        sigma = self.smoothing * 10
        return gaussian_filter1d(hist, sigma=sigma)

    def normalize_to_full_range(self, *histograms: np.ndarray) -> list[np.ndarray]:
        """Normalize histograms so the max value across all reaches 1.0."""
        max_val = max(h.max() for h in histograms)
        if max_val > 0:
            return [h / max_val for h in histograms]
        return list(histograms)

    @abstractmethod
    def render(self, data: HistogramData) -> RenderResult:
        """
        Render the histogram visualization.

        Args:
            data: Histogram data to visualize

        Returns:
            RenderResult containing PNG bytes and dimensions
        """
        pass

    def _save_figure_to_bytes(self, fig: plt.Figure) -> bytes:
        """Save matplotlib figure to PNG bytes."""
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=self.dpi, bbox_inches="tight", pad_inches=0.1)
        buf.seek(0)
        plt.close(fig)
        return buf.read()
