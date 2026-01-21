# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run server (auto-reloads on changes)
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/test_histogram.py

# Run a specific test
pytest tests/test_api.py::TestHistogramEndpoint::test_basic_histogram_generation -v

# Test the API manually
curl -X POST http://localhost:8000/api/v1/histogram \
  -F "image=@photo.jpg" \
  -F "style=neon_glow" \
  | jq -r '.image' | base64 -d > histogram.png
```

## Architecture

This is a FastAPI service that transforms images into artistic RGB histogram visualizations.

### Request Flow

1. **API Endpoint** (`app/api/v1/histogram.py`) - Accepts image upload, validates parameters
2. **Histogram Service** (`app/services/histogram.py`) - Calculates RGB histograms using NumPy, extracts dominant colors
3. **Renderer Service** (`app/services/renderer.py`) - Routes to appropriate style via `STYLE_REGISTRY`
4. **Style Classes** (`app/styles/`) - Each style extends `BaseStyle` and implements `render()`

### Adding New Styles

1. Create a new file in `app/styles/` extending `BaseStyle`
2. Implement the `render(data: HistogramData) -> RenderResult` method
3. Register in `STYLE_REGISTRY` in `app/services/renderer.py`
4. Add style name to `available_styles` in `app/core/config.py`
5. Add option to frontend dropdown in `app/static/index.html`

### Key Design Decisions

- **Matplotlib with Agg backend**: Required for server-side rendering without GUI (`matplotlib.use("Agg")` in `base.py`)
- **Golden ratio dimensions**: Output height is `width / 1.618`
- **Post-smoothing normalization**: Histograms are normalized after Gaussian smoothing to use full vertical range
- **Base64 response**: Images returned as base64 in JSON (no cloud storage in v0.1)

## Git Commits

Do not add "Co-Authored-By" or any self-promotional lines to commit messages.
