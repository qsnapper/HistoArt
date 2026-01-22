# HistoArt: Artistic RGB Histogram API

Every image has a color story. HistoArt reveals it. Upload any photo and receive a beautifully crafted histogram that's accurate enough for analysis and gorgeous enough to frame. Six artistic styles. One simple API.

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
- `minimal` - Ultra-clean lines with maximum whitespace and subtle colors
- `neon_glow` - Bold vibrant channels with luminous glow effects
- `original` - Classic histogram style with stippled fills
- `tron` - Neon curves with grid overlay
- `watercolor` - Soft, painterly aesthetic with irregular edges
