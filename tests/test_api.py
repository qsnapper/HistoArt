"""Tests for the histogram API endpoint."""

import base64
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_image_bytes():
    """Create a test image."""
    img = Image.new("RGB", (100, 100), (255, 128, 64))
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def large_test_image_bytes():
    """Create a larger test image for realistic testing."""
    img = Image.new("RGB", (800, 600))
    # Create a gradient
    pixels = img.load()
    for x in range(800):
        for y in range(600):
            pixels[x, y] = (x % 256, y % 256, (x + y) % 256)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestHistogramEndpoint:
    """Tests for histogram generation endpoint."""

    def test_basic_histogram_generation(self, client, test_image_bytes):
        """Test basic histogram generation with default parameters."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()

        # Check response structure
        assert "image" in data
        assert "metadata" in data

        # Check metadata
        assert "width" in data["metadata"]
        assert "height" in data["metadata"]
        assert "dominant_colors" in data["metadata"]
        assert "processing_time_ms" in data["metadata"]

        # Verify base64 image is valid
        image_bytes = base64.b64decode(data["image"])
        assert len(image_bytes) > 0

        # Verify it's a valid PNG
        img = Image.open(BytesIO(image_bytes))
        assert img.format == "PNG"

    def test_histogram_with_style(self, client, test_image_bytes):
        """Test histogram generation with specific style."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"style": "neon_glow"},
        )

        assert response.status_code == 200

    def test_histogram_with_custom_width(self, client, test_image_bytes):
        """Test histogram generation with custom width."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"width": 800},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["metadata"]["width"] == 800

    def test_histogram_with_smoothing(self, client, test_image_bytes):
        """Test histogram generation with custom smoothing."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"smoothing": 0.3},
        )

        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_image_format(self, client):
        """Test rejection of invalid image format."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.txt", b"not an image", "text/plain")},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_IMAGE"

    def test_invalid_style(self, client, test_image_bytes):
        """Test rejection of invalid style."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"style": "nonexistent_style"},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_STYLE"

    def test_invalid_width_too_small(self, client, test_image_bytes):
        """Test rejection of width below minimum."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"width": 50},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_WIDTH"

    def test_invalid_width_too_large(self, client, test_image_bytes):
        """Test rejection of width above maximum."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"width": 10000},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_WIDTH"

    def test_invalid_smoothing_negative(self, client, test_image_bytes):
        """Test rejection of negative smoothing value."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"smoothing": -0.5},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_SMOOTHING"

    def test_invalid_smoothing_too_high(self, client, test_image_bytes):
        """Test rejection of smoothing value above 1.0."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
            data={"smoothing": 1.5},
        )

        assert response.status_code == 400
        data = response.json()
        assert data["detail"]["error"] == "INVALID_SMOOTHING"


class TestDominantColors:
    """Tests for dominant color extraction in response."""

    def test_dominant_colors_included(self, client, test_image_bytes):
        """Test that dominant colors are included in response."""
        response = client.post(
            "/api/v1/histogram",
            files={"image": ("test.png", test_image_bytes, "image/png")},
        )

        assert response.status_code == 200
        data = response.json()

        dominant_colors = data["metadata"]["dominant_colors"]
        assert len(dominant_colors) > 0
        assert all(c.startswith("#") for c in dominant_colors)
