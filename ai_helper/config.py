from __future__ import annotations

from pathlib import Path

APP_NAME = "AI Helper"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
OLLAMA_MODEL = "deepseek-v3.1:671b-cloud"
APP_DATA_DIR = Path.home() / ".ai_helper"
DATABASE_DIR = APP_DATA_DIR / "databases"

for path in (APP_DATA_DIR, DATABASE_DIR):
    path.mkdir(parents=True, exist_ok=True)
