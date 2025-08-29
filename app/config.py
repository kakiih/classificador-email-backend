# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Mistral (remote) - preencha em .env
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "").strip()
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

# Local (fallback) model (TTL)
LOCAL_MODEL_NAME = os.getenv("LOCAL_MODEL_NAME", "nicholasKluge/TeenyTinyLlama-160m")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "120"))
