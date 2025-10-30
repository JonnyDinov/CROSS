from typing import Any, Dict, List, Optional

from modules.database import db


def _row_to_dict(row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "personality": row["personality"] or "",
        "speech_style": row["speech_style"] or "",
        "backstory": row["backstory"] or "",
        "world_role": row["world_role"] or "",
        "created_at": row["created_at"],
    }


def list_characters() -> List[Dict[str, Any]]:
    rows = db.fetchall("SELECT * FROM characters ORDER BY created_at DESC, id DESC")
    return [_row_to_dict(row) for row in rows]


def get_character(character_id: int) -> Optional[Dict[str, Any]]:
    row = db.fetchone("SELECT * FROM characters WHERE id = ?", (character_id,))
    return _row_to_dict(row) if row else None


def create_character(data: Dict[str, str]) -> int:
    cursor = db.execute(
        """
        INSERT INTO characters (name, personality, speech_style, backstory, world_role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            data.get("name", ""),
            data.get("personality", ""),
            data.get("speech_style", ""),
            data.get("backstory", ""),
            data.get("world_role", ""),
        ),
        commit=True,
    )
    return cursor.lastrowid


def update_character(character_id: int, data: Dict[str, str]) -> None:
    db.execute(
        """
        UPDATE characters
        SET name = ?, personality = ?, speech_style = ?, backstory = ?, world_role = ?
        WHERE id = ?
        """,
        (
            data.get("name", ""),
            data.get("personality", ""),
            data.get("speech_style", ""),
            data.get("backstory", ""),
            data.get("world_role", ""),
            character_id,
        ),
        commit=True,
    )


def delete_character(character_id: int) -> None:
    db.execute("DELETE FROM characters WHERE id = ?", (character_id,), commit=True)
