"""OpenRouter API service for LLM-based image generation."""

import base64
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


def transform_to_watercolor(input_image_bytes: bytes) -> bytes | None:
    """
    Transform a histogram image into watercolor style via OpenRouter.

    Uses img2img approach: passes the minimal histogram as input and asks
    the model to transform it while preserving the curve shapes.

    Args:
        input_image_bytes: PNG bytes of the minimal histogram to transform

    Returns:
        PNG image bytes of the transformed watercolor, or None if generation fails
    """
    if not settings.openrouter_api_key:
        logger.debug("No OpenRouter API key configured")
        return None

    # Encode input image as base64 data URL
    base64_image = base64.b64encode(input_image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{base64_image}"

    prompt = _build_transform_prompt()

    try:
        response = httpx.post(
            OPENROUTER_API_URL,
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.openrouter_image_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": data_url}},
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
                "modalities": ["image", "text"],
            },
            timeout=90.0,
        )
        response.raise_for_status()
        result = response.json()

        # Extract image from response
        choices = result.get("choices", [])
        if not choices:
            logger.warning("OpenRouter returned no choices")
            return None

        message = choices[0].get("message", {})
        images = message.get("images", [])
        if not images:
            logger.warning("OpenRouter returned no images")
            return None

        # Get base64 data URL
        image_url = images[0].get("image_url", {}).get("url", "")
        if not image_url.startswith("data:image/"):
            logger.warning("Invalid image URL format from OpenRouter")
            return None

        # Extract base64 data after the header
        # Format: "data:image/png;base64,iVBORw0KGgo..."
        _, base64_data = image_url.split(",", 1)
        return base64.b64decode(base64_data)

    except httpx.TimeoutException:
        logger.warning("OpenRouter request timed out")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"OpenRouter HTTP error: {e.response.status_code}")
        return None
    except Exception as e:
        logger.warning(f"OpenRouter error: {e}")
        return None


def _build_transform_prompt() -> str:
    """Build the image transformation prompt."""
    return """Transform this RGB histogram chart into a watercolor painting on textured paper.

CRITICAL: Preserve the three curve shapes, positions, and proportions. The red, green, and blue curves must remain in identical positions with the same relative heights.

FILL TREATMENT:
- Fill the entire area BENEATH each curve down to the baseline with watercolor wash
- Each channel (red, green, blue) should be a solid filled shape, like mountains rising from the bottom
- The top edge of each filled area follows the curve shape
- Avoid sharp, distinct edges - use diffuse, feathered boundaries
- Edges should appear to bleed into the surrounding paper
- Create a natural, fluid aesthetic with soft organic edges

TEXTURE AND FILL:
- Color fills should show variations in saturation (not uniform)
- Simulate watercolor granulation and wash effects
- Paint should appear translucent with visible paper texture through the washes

COLOR PALETTE (use these specific watercolor washes):
- Red channel: Deep burgundy (#4A0000) transitioning to vivid scarlet (#FF3333)
- Green channel: Forest green (#004A00) transitioning to electric lime (#33FF33)
- Blue channel: Navy blue (#00004A) transitioning to brilliant azure (#3333FF)

COLOR BLENDING:
- Where curves overlap, use additive color blending with reduced opacity
- Mimic how translucent watercolor pigments layer to create secondary colors
- Overlapping areas should show natural red, green, blue mixing

BACKGROUND:
- Pure white with subtle paper texture visible through the translucent paint
- Add a subtle vignette effect to frame the artwork
- Include generous padding around the histogram

Output only the transformed watercolor painting with no text, labels, or axes."""
