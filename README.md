# Artistic RGB Histogram API

Transform images into visually stunning RGB histogram visualizations.

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Run the server
uvicorn app.main:app --reload
```

## API Usage

```bash
curl -X POST http://localhost:8000/api/v1/histogram \
  -F "image=@photo.jpg" \
  -F "style=elegant_curves"
```

## Available Styles

- `elegant_curves` - Smooth bezier curves with subtle gradients
- `neon_glow` - Bold vibrant channels with luminous glow effects on dark background
