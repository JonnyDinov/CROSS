from __future__ import annotations

from typing import Any, Dict, List

from modules.database import db


def add_dialogue(character_id: int, player_line: str, ai_response: str) -> int:
    cursor = db.execute(
        """
        INSERT INTO dialogues (character_id, player_line, ai_response)
        VALUES (?, ?, ?)
        """,
        (character_id, player_line, ai_response),
        commit=True,
    )
    return cursor.lastrowid


def get_recent_dialogues(character_id: int, limit: int = 5) -> List[Dict[str, Any]]:
    rows = db.fetchall(
        """
        SELECT player_line, ai_response
        FROM dialogues
        WHERE character_id = ?
        ORDER BY created_at DESC, id DESC
        LIMIT ?
        """,
        (character_id, limit),
    )
    return [dict(row) for row in rows]
