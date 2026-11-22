import httpx

from backend.config import settings


def generate_response(prompt: str) -> str:

    url = f"{settings.OLLAMA_URL}/api/generate"

    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:

        response = httpx.post(
            url,
            json=payload,
            timeout=180.0
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]

    except httpx.HTTPError as error:

        raise RuntimeError(
            f"Ollama connection failed: {error}"
        ) from error