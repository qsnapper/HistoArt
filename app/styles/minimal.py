"""Minimal histogram style - ultra-clean lines with maximum whitespace and subtle colors."""

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class MinimalStyle(BaseStyle):
    """
    Ultra-clean lines with maximum whitespace and pure RGB colors.

    Features:
    - Transparent background
    - Thin, clean lines without glow effects
    - Pure RGB color palette
    - No fills or decorations
    """

    # Pure RGB colors
    MINIMAL_RED = "#FF0000"
    MINIMAL_GREEN = "#00FF00"
    MINIMAL_BLUE = "#0000FF"

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with minimal style."""
        # Create figure with golden ratio dimensions
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="none")
        ax.set_facecolor("none")

        # X values (0-255 for histogram bins)
        x = np.linspace(0, 255, 256)

        # Smooth the histograms and normalize to use full vertical range
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Draw clean lines - minimal style
        ax.plot(x, red_smooth, color=self.MINIMAL_RED, linewidth=3.5, alpha=0.9)
        ax.plot(x, green_smooth, color=self.MINIMAL_GREEN, linewidth=3.5, alpha=0.9)
        ax.plot(x, blue_smooth, color=self.MINIMAL_BLUE, linewidth=3.5, alpha=0.9)

        # Clean up axes
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 1.05)
        ax.axis("off")

        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        image_bytes = self._save_figure_to_bytes_transparent(fig)

        return RenderResult(
            image_bytes=image_bytes,
            width=self.width,
            height=self.height,
        )

    def _save_figure_to_bytes_transparent(self, fig: plt.Figure) -> bytes:
        """Save matplotlib figure to PNG bytes with alpha transparency."""
        buf = BytesIO()
        fig.savefig(
            buf,
            format="png",
            dpi=self.dpi,
            bbox_inches="tight",
            pad_inches=0,
            transparent=True,
            facecolor="none",
            edgecolor="none",
        )
        buf.seek(0)
        plt.close(fig)
        return buf.read()
