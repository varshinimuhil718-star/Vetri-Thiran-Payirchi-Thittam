from functools import lru_cache

from google import genai
from google.genai import types

from ..config import get_settings


@lru_cache
def get_gemini_client():
    settings = get_settings()

    if settings.mock_ai:
        return None

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured. Add it to .env, "
            "or set MOCK_AI=true to test without Gemini."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def generate_structured(*, model: str, prompt: str, response_schema, temperature: float = 0.4):
    client = get_gemini_client()
    if client is None:
        raise RuntimeError("Gemini client is unavailable because MOCK_AI=true.")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            response_mime_type="application/json",
            response_schema=response_schema,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text


def generate_text(*, model: str, prompt: str, temperature: float = 0.4) -> str:
    client = get_gemini_client()
    if client is None:
        raise RuntimeError("Gemini client is unavailable because MOCK_AI=true.")

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=1200,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text.strip()
