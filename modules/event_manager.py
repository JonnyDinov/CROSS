from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from modules.database import db


def _row_to_dict(row) -> Dict[str, Any]:
    involved = []
    if row["involved_characters"]:
        try:
            involved = json.loads(row["involved_characters"])
        except json.JSONDecodeError:
            involved = []
    return {
        "id": row["id"],
        "title": row["title"],
        "theme": row["theme"] or "",
        "narrative_style": row["narrative_style"] or "",
        "content": row["content"] or "",
        "involved_characters": involved,
        "created_at": row["created_at"],
    }


def list_events() -> List[Dict[str, Any]]:
    rows = db.fetchall("SELECT * FROM events ORDER BY created_at DESC, id DESC")
    return [_row_to_dict(row) for row in rows]


def get_event(event_id: int) -> Optional[Dict[str, Any]]:
    row = db.fetchone("SELECT * FROM events WHERE id = ?", (event_id,))
    return _row_to_dict(row) if row else None


def create_event(data: Dict[str, Any]) -> int:
    cursor = db.execute(
        """
        INSERT INTO events (title, theme, narrative_style, content, involved_characters)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.get("title", ""),
            data.get("theme", ""),
            data.get("narrative_style", ""),
            data.get("content", ""),
            json.dumps(data.get("involved_characters", [])),
        ),
        commit=True,
    )
    return cursor.lastrowid


def update_event(event_id: int, data: Dict[str, Any]) -> None:
    db.execute(
        """
        UPDATE events
        SET title = ?, theme = ?, narrative_style = ?, content = ?, involved_characters = ?
        WHERE id = ?
        """,
        (
            data.get("title", ""),
            data.get("theme", ""),
            data.get("narrative_style", ""),
            data.get("content", ""),
            json.dumps(data.get("involved_characters", [])),
            event_id,
        ),
        commit=True,
    )


def delete_event(event_id: int) -> None:
    db.execute("DELETE FROM events WHERE id = ?", (event_id,), commit=True)
