# src/config.py
import os
from dotenv import load_dotenv

class Settings:
    """
    Simple config loader: reads .env (via python-dotenv)
    and exposes FIRECRAWL_API_KEY, GEMINI_API_KEY, etc.
    """

    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)

        try:
            self.firecrawl_api_key = os.environ["FIRECRAWL_API_KEY"]
            self.gemini_api_key   = os.environ["GEMINI_API_KEY"]
        except KeyError as missing:
            raise RuntimeError(f"Missing required environment variable: {missing}") from None

        # Optional / with defaults:
        self.gemini_model = os.environ.get(
            "GEMINI_MODEL", "gemini-2.5-flash-preview-04-17"
        )
        self.default_limit = int(os.environ.get("DEFAULT_LIMIT", "5"))
