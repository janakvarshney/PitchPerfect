"""Portable LLM adapter — the single choke point for all model calls.

Swap providers with one env var (LLM_PROVIDER=groq|ollama). Nothing else in the
codebase knows or cares which model answered. Uses the OpenAI-compatible API that
both Groq and Ollama expose, so there is no provider-specific SDK lock-in.
"""

import json
import time
from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from .config import settings

T = TypeVar("T", bound=BaseModel)


def _chat(client: OpenAI, model: str, messages: list[dict], **kwargs):
    """Call chat.completions, falling back to FALLBACK_MODEL on a 429 (rate/quota).

    Groq's free tier caps tokens-per-day per model; the 70B writer model hits it
    first. Rather than fail, retry once on the smaller model's separate budget."""
    try:
        return client.chat.completions.create(model=model, messages=messages, **kwargs)
    except Exception as e:
        fb = settings.FALLBACK_MODEL
        msg = str(e).lower()
        if fb and fb != model and ("rate_limit" in msg or "429" in msg or "tokens per day" in msg):
            return client.chat.completions.create(model=fb, messages=messages, **kwargs)
        raise


def _client() -> OpenAI:
    if settings.LLM_PROVIDER == "ollama":
        # Ollama ignores the key but the SDK requires a non-empty string.
        return OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key="ollama")
    if not settings.GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Copy backend/.env.example to backend/.env and paste your key."
        )
    return OpenAI(base_url=settings.GROQ_BASE_URL, api_key=settings.GROQ_API_KEY)


def complete_text(
    prompt: str,
    *,
    model: str | None = None,
    system: str | None = None,
    temperature: float = 0.3,
) -> str:
    """Plain-text completion (no JSON mode). Used for outputs like LaTeX where
    JSON escaping would mangle backslashes."""
    client = _client()
    model = model or settings.DEFAULT_MODEL
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = _chat(client, model, messages, temperature=temperature)
    return (resp.choices[0].message.content or "").strip()


def complete_json(
    prompt: str,
    schema: Type[T],
    *,
    model: str | None = None,
    system: str | None = None,
    temperature: float = 0.3,
    max_retries: int = 2,
) -> T:
    """Call the LLM and return a validated Pydantic object.

    Uses JSON mode and embeds the target JSON schema in the system prompt (this
    also guarantees the word "json" is present, which Groq's JSON mode requires).
    On a validation failure it feeds the error back to the model and retries.
    """
    client = _client()
    model = model or settings.DEFAULT_MODEL

    schema_json = json.dumps(schema.model_json_schema())
    system_prompt = (system + "\n\n" if system else "") + (
        "You are a precise information-extraction engine. "
        "Respond with ONLY a single JSON object that conforms to this JSON schema:\n"
        f"{schema_json}\n"
        "Do not include markdown fences or any prose outside the JSON object."
    )

    messages: list[dict] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]

    last_error: Exception | None = None
    for attempt in range(max_retries + 1):
        resp = _chat(
            client,
            model,
            messages,
            response_format={"type": "json_object"},
            temperature=temperature,
        )
        content = resp.choices[0].message.content or "{}"
        try:
            return schema.model_validate_json(content)
        except ValidationError as e:
            last_error = e
            messages.append({"role": "assistant", "content": content})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "That JSON did not match the schema. Validation errors:\n"
                        f"{e}\nReturn ONLY corrected JSON matching the schema."
                    ),
                }
            )
            time.sleep(0.5 * (attempt + 1))

    raise ValueError(f"LLM failed to produce valid {schema.__name__}: {last_error}")
