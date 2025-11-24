# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self) -> None:
        # API key Gemini dari environment / .env
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


settings = Settings()
