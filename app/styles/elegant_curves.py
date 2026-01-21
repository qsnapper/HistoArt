"""Elegant curves histogram style - smooth curves with rich vertical gradients."""

from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class ElegantCurvesStyle(BaseStyle):
    """
    Smooth curves with rich vertical gradients and beautiful color blending.

    Features:
    - Smooth curve interpolation
    - Rich vertical gradients from dark to vibrant for each channel
    - Semi-transparent fills that blend where curves overlap
    - Transparent background
    """

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with elegant curves style."""
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

        # Draw gradient fills for each channel
        self._draw_gradient_fill(ax, x, red_smooth, self.RED_DARK, self.RED_LIGHT)
        self._draw_gradient_fill(ax, x, green_smooth, self.GREEN_DARK, self.GREEN_LIGHT)
        self._draw_gradient_fill(ax, x, blue_smooth, self.BLUE_DARK, self.BLUE_LIGHT)

        # Clean up axes
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 1.0)
        ax.axis("off")

        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        image_bytes = self._save_figure_to_bytes_transparent(fig)

        return RenderResult(
            image_bytes=image_bytes,
            width=self.width,
            height=self.height,
        )

    def _draw_gradient_fill(
        self,
        ax: plt.Axes,
        x: np.ndarray,
        y: np.ndarray,
        dark_color: str,
        light_color: str,
    ):
        """
        Draw a curve with vertical gradient fill using imshow clipped to curve path.

        Creates a gradient image from dark (bottom) to light (top) and clips it
        to the area under the curve using a polygon clip path.
        """
        from matplotlib.patches import Polygon

        # Create the gradient image (vertical gradient from dark to light)
        gradient = np.linspace(0, 1, 256).reshape(-1, 1)
        gradient = np.hstack([gradient] * 256)

        # Create colormap from dark to light
        cmap = LinearSegmentedColormap.from_list("gradient", [dark_color, light_color])

        # Display the gradient image
        im = ax.imshow(
            gradient,
            aspect="auto",
            extent=[0, 255, 0, 1],
            origin="lower",
            cmap=cmap,
            alpha=0.85,
        )

        # Create clip path from the curve
        # Build polygon: curve points + bottom corners
        verts = list(zip(x, y))
        verts.append((255, 0))  # Bottom right
        verts.append((0, 0))    # Bottom left
        poly = Polygon(verts, closed=True, transform=ax.transData)

        # Clip the gradient image to the curve shape
        im.set_clip_path(poly)

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
