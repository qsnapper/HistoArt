"""Tests for histogram calculation service."""

import numpy as np
from PIL import Image
from io import BytesIO

from app.services.histogram import calculate_histogram, extract_dominant_colors


def create_test_image(color: tuple[int, int, int], size: tuple[int, int] = (100, 100)) -> bytes:
    """Create a solid color test image."""
    img = Image.new("RGB", size, color)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def create_gradient_image(size: tuple[int, int] = (256, 100)) -> bytes:
    """Create a horizontal gradient test image."""
    img = Image.new("RGB", size)
    pixels = img.load()
    for x in range(size[0]):
        for y in range(size[1]):
            pixels[x, y] = (x, x, x)  # Grayscale gradient
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


class TestHistogramCalculation:
    """Tests for histogram calculation."""

    def test_solid_red_image(self):
        """Test histogram of solid red image."""
        image_bytes = create_test_image((255, 0, 0))
        result = calculate_histogram(image_bytes)

        # Red channel should have all values at 255
        assert result.red[255] == 1.0
        assert np.sum(result.red[:255]) == 0.0

        # Green and blue should have all values at 0
        assert result.green[0] == 1.0
        assert result.blue[0] == 1.0

    def test_solid_green_image(self):
        """Test histogram of solid green image."""
        image_bytes = create_test_image((0, 255, 0))
        result = calculate_histogram(image_bytes)

        assert result.green[255] == 1.0
        assert result.red[0] == 1.0
        assert result.blue[0] == 1.0

    def test_solid_blue_image(self):
        """Test histogram of solid blue image."""
        image_bytes = create_test_image((0, 0, 255))
        result = calculate_histogram(image_bytes)

        assert result.blue[255] == 1.0
        assert result.red[0] == 1.0
        assert result.green[0] == 1.0

    def test_gradient_image(self):
        """Test histogram of gradient image has distributed values."""
        image_bytes = create_gradient_image()
        result = calculate_histogram(image_bytes)

        # Should have non-zero values across the histogram
        assert np.sum(result.red > 0) > 100
        assert np.sum(result.green > 0) > 100
        assert np.sum(result.blue > 0) > 100

    def test_dominant_colors_solid(self):
        """Test dominant color extraction from solid image."""
        image_bytes = create_test_image((255, 0, 0))
        result = calculate_histogram(image_bytes)

        # Should have red as dominant color
        assert len(result.dominant_colors) > 0
        # The dominant color should be close to red (quantized)
        assert result.dominant_colors[0].startswith("#F")

    def test_histogram_shape(self):
        """Test that histograms have correct shape."""
        image_bytes = create_test_image((128, 128, 128))
        result = calculate_histogram(image_bytes)

        assert result.red.shape == (256,)
        assert result.green.shape == (256,)
        assert result.blue.shape == (256,)

    def test_histogram_normalized(self):
        """Test that histograms are normalized to 0-1 range."""
        image_bytes = create_test_image((128, 128, 128))
        result = calculate_histogram(image_bytes)

        assert result.red.max() <= 1.0
        assert result.green.max() <= 1.0
        assert result.blue.max() <= 1.0
        assert result.red.min() >= 0.0
        assert result.green.min() >= 0.0
        assert result.blue.min() >= 0.0


class TestDominantColors:
    """Tests for dominant color extraction."""

    def test_extracts_correct_count(self):
        """Test that correct number of colors are extracted."""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        colors = extract_dominant_colors(img, n_colors=5)
        assert len(colors) <= 5

    def test_returns_hex_format(self):
        """Test that colors are returned in hex format."""
        img = np.full((100, 100, 3), 128, dtype=np.uint8)
        colors = extract_dominant_colors(img, n_colors=3)

        for color in colors:
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB format
