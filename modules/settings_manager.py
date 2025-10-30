from __future__ import annotations

import json
from typing import Any, Dict

from modules.database import db


BOOLEAN_KEYS = {"save_dialogue_context"}


def _deserialize_value(key: str, value: str) -> Any:
    if key in BOOLEAN_KEYS:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value.lower() in {"true", "1", "yes"}
    return value


def _serialize_value(key: str, value: Any) -> str:
    if key in BOOLEAN_KEYS:
        return json.dumps(bool(value))
    return str(value)


def get_settings() -> Dict[str, Any]:
    rows = db.fetchall("SELECT key, value FROM settings")
    raw = {row["key"]: row["value"] for row in rows}

    settings = {
        "ollama_url": raw.get("ollama_url", "http://localhost:11434"),
        "model": raw.get("model", "llama2"),
        "global_style": raw.get("global_style", ""),
        "save_dialogue_context": _deserialize_value(
            "save_dialogue_context", raw.get("save_dialogue_context", "true")
        ),
    }
    return settings


def update_settings(changes: Dict[str, Any]) -> None:
    for key, value in changes.items():
        db.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, _serialize_value(key, value)),
            commit=True,
        )
