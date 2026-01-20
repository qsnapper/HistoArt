"""Core histogram calculation service."""

from collections import Counter
from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image


@dataclass
class HistogramData:
    """RGB histogram data."""

    red: np.ndarray  # 256 bins
    green: np.ndarray  # 256 bins
    blue: np.ndarray  # 256 bins
    dominant_colors: list[str]  # Top 5 hex colors


def calculate_histogram(image_bytes: bytes) -> HistogramData:
    """
    Calculate RGB histogram from image bytes.

    Args:
        image_bytes: Raw image file bytes

    Returns:
        HistogramData containing histogram arrays and dominant colors
    """
    image = Image.open(BytesIO(image_bytes))

    # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Convert to numpy array
    img_array = np.array(image)

    # Calculate histogram for each channel (256 bins, values 0-255)
    red_hist, _ = np.histogram(img_array[:, :, 0].flatten(), bins=256, range=(0, 256))
    green_hist, _ = np.histogram(img_array[:, :, 1].flatten(), bins=256, range=(0, 256))
    blue_hist, _ = np.histogram(img_array[:, :, 2].flatten(), bins=256, range=(0, 256))

    # Normalize histograms to 0-1 range
    max_val = max(red_hist.max(), green_hist.max(), blue_hist.max())
    if max_val > 0:
        red_hist = red_hist.astype(float) / max_val
        green_hist = green_hist.astype(float) / max_val
        blue_hist = blue_hist.astype(float) / max_val

    # Extract dominant colors
    dominant_colors = extract_dominant_colors(img_array, n_colors=5)

    return HistogramData(
        red=red_hist,
        green=green_hist,
        blue=blue_hist,
        dominant_colors=dominant_colors,
    )


def extract_dominant_colors(img_array: np.ndarray, n_colors: int = 5) -> list[str]:
    """
    Extract dominant colors from image using color quantization.

    Args:
        img_array: Numpy array of RGB image
        n_colors: Number of dominant colors to extract

    Returns:
        List of hex color strings
    """
    # Resize image for faster processing
    h, w = img_array.shape[:2]
    scale = min(1.0, 100 / max(h, w))
    if scale < 1.0:
        new_h, new_w = int(h * scale), int(w * scale)
        img_small = Image.fromarray(img_array).resize((new_w, new_h), Image.Resampling.LANCZOS)
        img_array = np.array(img_small)

    # Flatten to list of pixels and quantize to reduce color space
    pixels = img_array.reshape(-1, 3)
    # Quantize to 32 levels per channel for faster counting
    quantized = (pixels // 8) * 8

    # Count colors
    color_tuples = [tuple(p) for p in quantized]
    color_counts = Counter(color_tuples)

    # Get most common colors
    most_common = color_counts.most_common(n_colors)

    # Convert to hex
    hex_colors = []
    for color, _ in most_common:
        r, g, b = color
        hex_colors.append(f"#{r:02X}{g:02X}{b:02X}")

    return hex_colors
