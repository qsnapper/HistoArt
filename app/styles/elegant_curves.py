"""Elegant curves histogram style - smooth bezier curves with subtle gradients."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class ElegantCurvesStyle(BaseStyle):
    """
    Smooth bezier curves with subtle gradients and refined aesthetics.

    Features:
    - Smooth curve interpolation
    - Gradient fills from dark to vibrant for each channel
    - Additive blending for overlapping regions
    - White background with clean styling
    """

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with elegant curves style."""
        # Create figure with golden ratio dimensions
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor="white")
        ax.set_facecolor("white")

        # X values (0-255 for histogram bins)
        x = np.linspace(0, 255, 256)

        # Smooth the histograms and normalize to use full vertical range
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Create gradient colormaps for each channel
        red_cmap = LinearSegmentedColormap.from_list("red", [self.RED_DARK, self.RED_LIGHT])
        green_cmap = LinearSegmentedColormap.from_list("green", [self.GREEN_DARK, self.GREEN_LIGHT])
        blue_cmap = LinearSegmentedColormap.from_list("blue", [self.BLUE_DARK, self.BLUE_LIGHT])

        # Plot each channel with gradient fill and transparency for blending
        self._plot_gradient_fill(ax, x, red_smooth, red_cmap, alpha=0.6)
        self._plot_gradient_fill(ax, x, green_smooth, green_cmap, alpha=0.6)
        self._plot_gradient_fill(ax, x, blue_smooth, blue_cmap, alpha=0.6)

        # Add subtle curve outlines
        ax.plot(x, red_smooth, color=self.RED_LIGHT, linewidth=1.5, alpha=0.8)
        ax.plot(x, green_smooth, color=self.GREEN_LIGHT, linewidth=1.5, alpha=0.8)
        ax.plot(x, blue_smooth, color=self.BLUE_LIGHT, linewidth=1.5, alpha=0.8)

        # Clean up axes for aesthetic look
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 1.05)
        ax.axis("off")

        # Add subtle padding
        fig.tight_layout(pad=0.5)

        # Save to bytes
        image_bytes = self._save_figure_to_bytes(fig)

        return RenderResult(
            image_bytes=image_bytes,
            width=self.width,
            height=self.height,
        )

    def _plot_gradient_fill(
        self,
        ax: plt.Axes,
        x: np.ndarray,
        y: np.ndarray,
        cmap: LinearSegmentedColormap,
        alpha: float = 0.6,
    ):
        """
        Plot a curve with gradient fill from bottom to top.

        Uses imshow to create vertical gradient effect under the curve.
        """
        # Create a mesh for the gradient
        # We'll use many thin rectangles to approximate the gradient fill
        n_segments = 100
        for i in range(n_segments):
            # Calculate the y range for this segment
            y_bottom = i / n_segments
            y_top = (i + 1) / n_segments

            # Get color for this height level
            color = cmap(i / n_segments)

            # Fill only where the histogram is above this level
            mask = y >= y_top
            if np.any(mask):
                # Create filled region
                y_fill = np.where(y >= y_top, y_top, y)
                y_fill = np.maximum(y_fill, y_bottom)
                ax.fill_between(
                    x,
                    y_bottom,
                    y_fill,
                    where=(y >= y_bottom),
                    color=color,
                    alpha=alpha / n_segments * 3,  # Adjust alpha for layering
                    linewidth=0,
                )
