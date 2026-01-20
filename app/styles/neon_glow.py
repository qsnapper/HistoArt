"""Neon glow histogram style - bold vibrant channels with luminous glow effects."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba

from app.services.histogram import HistogramData
from app.styles.base import BaseStyle, RenderResult


class NeonGlowStyle(BaseStyle):
    """
    Bold, vibrant channels with luminous glow effects on dark background.

    Features:
    - Dark charcoal background
    - Bright neon colors for RGB channels
    - Multiple layered glows for bloom effect
    - High contrast visualization
    """

    # Neon colors (brighter than standard)
    NEON_RED = "#FF0040"
    NEON_GREEN = "#00FF80"
    NEON_BLUE = "#0080FF"

    # Background
    BACKGROUND = "#1A1A2E"

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with neon glow style."""
        # Create figure with golden ratio dimensions
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor=self.BACKGROUND)
        ax.set_facecolor(self.BACKGROUND)

        # X values (0-255 for histogram bins)
        x = np.linspace(0, 255, 256)

        # Smooth the histograms and normalize to use full vertical range
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Draw glow layers (multiple passes with decreasing alpha and increasing linewidth)
        glow_layers = [
            (20, 0.05),
            (15, 0.08),
            (10, 0.12),
            (6, 0.18),
            (3, 0.3),
        ]

        for linewidth, alpha in glow_layers:
            ax.plot(x, red_smooth, color=self.NEON_RED, linewidth=linewidth, alpha=alpha)
            ax.plot(x, green_smooth, color=self.NEON_GREEN, linewidth=linewidth, alpha=alpha)
            ax.plot(x, blue_smooth, color=self.NEON_BLUE, linewidth=linewidth, alpha=alpha)

        # Draw main lines on top
        ax.plot(x, red_smooth, color=self.NEON_RED, linewidth=2, alpha=1.0)
        ax.plot(x, green_smooth, color=self.NEON_GREEN, linewidth=2, alpha=1.0)
        ax.plot(x, blue_smooth, color=self.NEON_BLUE, linewidth=2, alpha=1.0)

        # Add subtle fill under curves
        ax.fill_between(x, 0, red_smooth, color=self.NEON_RED, alpha=0.15)
        ax.fill_between(x, 0, green_smooth, color=self.NEON_GREEN, alpha=0.15)
        ax.fill_between(x, 0, blue_smooth, color=self.NEON_BLUE, alpha=0.15)

        # Clean up axes
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
