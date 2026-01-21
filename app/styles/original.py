"""Original histogram style - classic RGB curves with transparent background."""

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class OriginalStyle(BaseStyle):
    """
    Classic RGB histogram with transparent background and stippled fills.

    Features:
    - Transparent (alpha channel) background for PNG output
    - Three independent RGB color histogram curves
    - Thick solid line strokes
    - Stippled/dotted fill pattern (screen-print friendly for t-shirts)
    """

    # RGB colors matched to reference (softer, screen-print aesthetic)
    RGB_RED = "#E85A5A"
    RGB_GREEN = "#4AE88A"
    RGB_BLUE = "#5A7ABF"

    # Style parameters
    LINE_WIDTH = 2.5
    # Hatch pattern: dots for stippled effect (repeat for density)
    HATCH_PATTERN = "..."

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with classic RGB style and transparent background."""
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi

        # Create figure with transparent background
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="none")
        ax.set_facecolor("none")

        x = np.linspace(0, 255, 256)

        # Smooth and normalize histograms
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Draw fills with hatch pattern (no solid fill, just hatching)
        ax.fill_between(
            x, 0, red_smooth,
            facecolor="none",
            edgecolor=self.RGB_RED,
            hatch=self.HATCH_PATTERN,
            linewidth=0,
        )
        ax.fill_between(
            x, 0, green_smooth,
            facecolor="none",
            edgecolor=self.RGB_GREEN,
            hatch=self.HATCH_PATTERN,
            linewidth=0,
        )
        ax.fill_between(
            x, 0, blue_smooth,
            facecolor="none",
            edgecolor=self.RGB_BLUE,
            hatch=self.HATCH_PATTERN,
            linewidth=0,
        )

        # Draw lines on top
        ax.plot(x, red_smooth, color=self.RGB_RED, linewidth=self.LINE_WIDTH)
        ax.plot(x, green_smooth, color=self.RGB_GREEN, linewidth=self.LINE_WIDTH)
        ax.plot(x, blue_smooth, color=self.RGB_BLUE, linewidth=self.LINE_WIDTH)

        # Clean minimal design - no axes
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
