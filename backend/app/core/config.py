import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the backend directory
backend_dir = Path(__file__).parent.parent.parent  # app/core/config.py -> backend
env_path = backend_dir / ".env"
load_dotenv(env_path)


class Settings:
    """App configuration, loaded from environment / .env.

    Everything the LLM adapter needs to switch providers lives here, so no
    agent or route code ever hardcodes a provider.
    """

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq").lower()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    # Cheap/fast model for extraction + matching; stronger model for writing.
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "groq/compound-mini")
    WRITER_MODEL: str = os.getenv("WRITER_MODEL", "groq/compound-mini")
    # Used when the primary model returns 429 (rate/quota limit). Has a separate,
    # larger free-tier budget so the app keeps working when the 70B cap is hit.
    FALLBACK_MODEL: str = os.getenv("FALLBACK_MODEL", "groq/compound-mini")

    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",") if o.strip()
    ]


settings = Settings()
