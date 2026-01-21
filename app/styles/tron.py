"""Tron histogram style - neon curves with grid on black background."""

import matplotlib.pyplot as plt
import numpy as np

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class TronStyle(BaseStyle):
    """
    Tron-inspired visualization with glowing neon curves on black background.

    Features:
    - Pure black background
    - Cyan grid pattern
    - Dashed cyan border frame
    - Bright neon RGB curves with glow effect
    """

    # Colors - bright saturated neons
    BACKGROUND = "#000000"
    GRID_COLOR = "#00FFFF"
    NEON_RED = "#FF0000"
    NEON_GREEN = "#00FF00"
    NEON_BLUE = "#0066FF"

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with Tron style."""
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor=self.BACKGROUND)
        ax.set_facecolor(self.BACKGROUND)

        x = np.linspace(0, 255, 256)

        # Smooth and normalize histograms
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Set up axes
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 1.05)
        ax.axis("off")

        # Use zorder to control layering explicitly
        # zorder 1: grid lines, zorder 2: mask, zorder 3+: curve glow/lines, zorder 5: border

        grid_dash = (8, 6)
        grid_color_bright = "#00FFFF"  # Bright cyan

        # Grid lines (zorder=1) - clean dashed lines
        for x_pos in np.linspace(0, 255, 5)[1:-1]:
            ax.axvline(x=x_pos, color=grid_color_bright, alpha=0.5,
                       linewidth=1.0, linestyle="--", dashes=grid_dash, zorder=1)

        for y_pos in np.linspace(0, 1.05, 4)[1:-1]:
            ax.axhline(y=y_pos, color=grid_color_bright, alpha=0.5,
                       linewidth=1.0, linestyle="--", dashes=grid_dash, zorder=1)

        # Border frame (zorder=5 - on top of everything)
        from matplotlib.patches import Rectangle
        border = Rectangle((0, 0), 255, 1.05, fill=False,
                           edgecolor=grid_color_bright, linewidth=1.5,
                           linestyle="--", alpha=0.8, zorder=5)
        border.set_linestyle((0, (8, 6)))  # Match grid dash pattern
        ax.add_patch(border)

        # Black mask using Polygon for guaranteed opacity (zorder=2)
        from matplotlib.patches import Polygon
        combined_max = np.maximum(np.maximum(red_smooth, green_smooth), blue_smooth)
        verts = [(x[0], 0)] + list(zip(x, combined_max)) + [(x[-1], 0)]
        mask_poly = Polygon(verts, facecolor=self.BACKGROUND, edgecolor='none', zorder=2)
        ax.add_patch(mask_poly)

        # Glow layers (zorder=3)
        glow_layers = [
            (30, 0.03),
            (24, 0.05),
            (18, 0.08),
            (12, 0.12),
            (8, 0.18),
            (5, 0.25),
            (3, 0.4),
        ]

        for linewidth, alpha in glow_layers:
            ax.plot(x, red_smooth, color=self.NEON_RED, linewidth=linewidth, alpha=alpha, zorder=3)
            ax.plot(x, green_smooth, color=self.NEON_GREEN, linewidth=linewidth, alpha=alpha, zorder=3)
            ax.plot(x, blue_smooth, color=self.NEON_BLUE, linewidth=linewidth, alpha=alpha, zorder=3)

        # Main lines (zorder=4)
        ax.plot(x, red_smooth, color="#FFFFFF", linewidth=1.5, alpha=0.6, zorder=4)
        ax.plot(x, green_smooth, color="#FFFFFF", linewidth=1.5, alpha=0.6, zorder=4)
        ax.plot(x, blue_smooth, color="#FFFFFF", linewidth=1.5, alpha=0.6, zorder=4)
        ax.plot(x, red_smooth, color=self.NEON_RED, linewidth=2.5, alpha=1.0, zorder=4)
        ax.plot(x, green_smooth, color=self.NEON_GREEN, linewidth=2.5, alpha=1.0, zorder=4)
        ax.plot(x, blue_smooth, color=self.NEON_BLUE, linewidth=2.5, alpha=1.0, zorder=4)

        fig.tight_layout(pad=0.5)

        image_bytes = self._save_figure_to_bytes(fig)

        return RenderResult(
            image_bytes=image_bytes,
            width=self.width,
            height=self.height,
        )
