"""Watercolor histogram style - soft organic edges mimicking watercolor paint."""

import logging

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from scipy.ndimage import gaussian_filter1d

from app.services.histogram import HistogramData
from app.services.openrouter import transform_to_watercolor
from app.styles.base import BaseStyle, RenderResult
from app.styles.minimal import MinimalStyle

logger = logging.getLogger(__name__)


class WatercolorStyle(BaseStyle):
    """
    Soft, organic edges mimicking watercolor paint bleeding.

    Uses LLM-based image generation via OpenRouter when available,
    falling back to matplotlib rendering otherwise.

    Features:
    - Irregular/ragged top edges like paint bleeding on paper
    - Rich color gradients from dark to saturated
    - Cream/paper-like background
    - Soft blending where colors overlap
    - No hard outlines
    """

    # Watercolor palette - rich, saturated colors
    RED_DARK = "#8B0000"  # Dark red
    RED_LIGHT = "#DC143C"  # Crimson
    GREEN_DARK = "#006400"  # Dark green
    GREEN_LIGHT = "#32CD32"  # Lime green
    BLUE_DARK = "#00008B"  # Dark blue
    BLUE_LIGHT = "#4169E1"  # Royal blue

    # Paper background color
    PAPER_COLOR = "#F5F5DC"  # Beige/cream

    def render(self, data: HistogramData) -> RenderResult:
        """Render histogram with watercolor style."""
        # Try LLM-based generation first
        llm_result = self._try_llm_generation(data)
        if llm_result:
            return llm_result

        # Fall back to matplotlib rendering
        return self._render_matplotlib(data)

    def _try_llm_generation(self, data: HistogramData) -> RenderResult | None:
        """Attempt to generate watercolor image via OpenRouter img2img."""
        try:
            # First, render the minimal histogram as the input reference
            minimal = MinimalStyle(width=self.width, smoothing=self.smoothing)
            minimal_result = minimal.render(data)

            # Transform it to watercolor style
            image_bytes = transform_to_watercolor(
                input_image_bytes=minimal_result.image_bytes,
                dominant_colors=data.dominant_colors,
            )
            if image_bytes:
                logger.info("Transformed histogram to watercolor via OpenRouter")
                return RenderResult(
                    image_bytes=image_bytes,
                    width=self.width,
                    height=self.height,
                )
        except Exception as e:
            logger.warning(f"LLM transformation failed: {e}")
        return None

    def _render_matplotlib(self, data: HistogramData) -> RenderResult:
        """Render histogram using matplotlib (fallback)."""
        fig_width = self.width / self.dpi
        fig_height = self.height / self.dpi
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), facecolor=self.PAPER_COLOR)
        ax.set_facecolor(self.PAPER_COLOR)

        x = np.linspace(0, 255, 256)

        # Smooth the histograms
        red_smooth = self.smooth_histogram(data.red)
        green_smooth = self.smooth_histogram(data.green)
        blue_smooth = self.smooth_histogram(data.blue)
        red_smooth, green_smooth, blue_smooth = self.normalize_to_full_range(
            red_smooth, green_smooth, blue_smooth
        )

        # Add irregular edges to simulate watercolor bleeding
        red_watercolor = self._add_watercolor_edge(red_smooth)
        green_watercolor = self._add_watercolor_edge(green_smooth)
        blue_watercolor = self._add_watercolor_edge(blue_smooth)

        # Create gradient colormaps
        red_cmap = LinearSegmentedColormap.from_list(
            "red", [self.PAPER_COLOR, self.RED_DARK, self.RED_LIGHT]
        )
        green_cmap = LinearSegmentedColormap.from_list(
            "green", [self.PAPER_COLOR, self.GREEN_DARK, self.GREEN_LIGHT]
        )
        blue_cmap = LinearSegmentedColormap.from_list(
            "blue", [self.PAPER_COLOR, self.BLUE_DARK, self.BLUE_LIGHT]
        )

        # Draw watercolor fills with soft blending
        self._draw_watercolor_fill(ax, x, red_watercolor, red_cmap, alpha=0.7)
        self._draw_watercolor_fill(ax, x, green_watercolor, green_cmap, alpha=0.7)
        self._draw_watercolor_fill(ax, x, blue_watercolor, blue_cmap, alpha=0.7)

        # Clean up axes
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 1.05)
        ax.axis("off")

        fig.tight_layout(pad=0.5)

        image_bytes = self._save_figure_to_bytes(fig)

        return RenderResult(
            image_bytes=image_bytes,
            width=self.width,
            height=self.height,
        )

    def _add_watercolor_edge(self, hist: np.ndarray) -> np.ndarray:
        """Add irregular edges to histogram to simulate watercolor bleeding."""
        # Create random variations for the edge
        np.random.seed(42)  # Consistent results
        noise = np.random.randn(len(hist)) * 0.05

        # Smooth the noise so variations are gradual
        noise_smooth = gaussian_filter1d(noise, sigma=3)

        # Apply noise to the histogram values
        result = hist + noise_smooth * hist

        # Ensure values stay in valid range
        result = np.clip(result, 0, 1)

        return result

    def _draw_watercolor_fill(
        self,
        ax: plt.Axes,
        x: np.ndarray,
        y: np.ndarray,
        cmap: LinearSegmentedColormap,
        alpha: float = 0.7,
    ):
        """
        Draw a watercolor-style filled area with vertical gradient.

        Creates the effect of paint pooling darker at the bottom
        and lighter/more saturated at the top.
        """
        n_layers = 50

        for i in range(n_layers):
            # Calculate the y range for this layer
            y_bottom = i / n_layers
            y_top = (i + 1) / n_layers

            # Get color for this height - darker at bottom, lighter at top
            color = cmap(0.3 + 0.7 * (i / n_layers))

            # Create the fill with soft edges
            y_fill = np.clip(y, y_bottom, y_top)

            ax.fill_between(
                x,
                y_bottom,
                y_fill,
                where=(y >= y_bottom),
                color=color,
                alpha=alpha / n_layers * 2.5,
                linewidth=0,
            )

        # Add a very subtle darker edge at the top for definition
        ax.fill_between(
            x,
            y * 0.98,
            y,
            color=cmap(0.5),
            alpha=0.15,
            linewidth=0,
        )
