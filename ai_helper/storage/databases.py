from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable, Optional

from ai_helper import models
from ai_helper.config import DATABASE_DIR


CREATE_STATEMENTS = {
    "characters": [
        """
        CREATE TABLE IF NOT EXISTS characters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            description TEXT,
            voice TEXT,
            goals TEXT,
            traits TEXT,
            bio TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            relation TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE CASCADE,
            FOREIGN KEY(target_id) REFERENCES characters(id) ON DELETE CASCADE
        )
        """,
    ],
    "quests": [
        """
        CREATE TABLE IF NOT EXISTS quests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            genre TEXT,
            characters TEXT,
            difficulty TEXT,
            rewards TEXT,
            json TEXT
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS quest_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quest_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(quest_id) REFERENCES quests(id) ON DELETE CASCADE
        )
        """,
    ],
    "books": [
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT,
            chars_per_page INTEGER NOT NULL DEFAULT 2000,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            page_number INTEGER NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY(book_id) REFERENCES books(id) ON DELETE CASCADE
        )
        """,
    ],
    "styles": [
        """
        CREATE TABLE IF NOT EXISTS styles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            yaml_rules TEXT,
            active INTEGER NOT NULL DEFAULT 1
        )
        """,
    ],
    "roleplay": [
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            character_id INTEGER NOT NULL,
            setting TEXT,
            start_time TEXT DEFAULT CURRENT_TIMESTAMP,
            user_goals TEXT,
            FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE SET NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS dialogue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            speaker TEXT NOT NULL,
            message TEXT NOT NULL,
            edited INTEGER NOT NULL DEFAULT 0,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS character_state (
            session_id INTEGER PRIMARY KEY,
            mood TEXT,
            memory TEXT,
            notes TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
        )
        """,
    ],
    "history": [
        """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time TEXT DEFAULT CURRENT_TIMESTAMP,
            user_text TEXT,
            result_text TEXT,
            style_applied TEXT,
            session_id INTEGER
        )
        """,
    ],
}


class DatabaseManager:
    """Simple multi-database manager using SQLite."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = Path(base_dir or DATABASE_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._connections: dict[str, sqlite3.Connection] = {}
        self._init_databases()

    def _init_databases(self) -> None:
        for name, statements in CREATE_STATEMENTS.items():
            conn = self._get_connection(name)
            with conn:
                for statement in statements:
                    conn.execute(statement)

    def _get_connection(self, name: str) -> sqlite3.Connection:
        if name not in self._connections:
            db_path = self.base_dir / f"{name}.db"
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            self._connections[name] = conn
        return self._connections[name]

    @contextmanager
    def connection(self, name: str):
        conn = self._get_connection(name)
        try:
            yield conn
        finally:
            conn.commit()

    def add_style(self, style: models.Style) -> models.Style:
        with self.connection("styles") as conn:
            cursor = conn.execute(
                "INSERT INTO styles (name, description, yaml_rules, active) VALUES (?, ?, ?, ?)",
                (style.name, style.description, style.yaml_rules, int(style.active)),
            )
            style.id = cursor.lastrowid
        return style

    def get_styles(self) -> list[models.Style]:
        with self.connection("styles") as conn:
            rows = conn.execute(
                "SELECT id, name, description, yaml_rules, active FROM styles ORDER BY name"
            ).fetchall()
        return [
            models.Style(
                id=row["id"],
                name=row["name"],
                description=row["description"],
                yaml_rules=row["yaml_rules"],
                active=bool(row["active"]),
            )
            for row in rows
        ]

    def add_character(self, character: models.Character) -> models.Character:
        with self.connection("characters") as conn:
            cursor = conn.execute(
                """
                INSERT INTO characters (name, age, gender, description, voice, goals, traits, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    character.name,
                    character.age,
                    character.gender,
                    character.description,
                    character.voice,
                    character.goals,
                    character.traits,
                    character.bio,
                ),
            )
            character.id = cursor.lastrowid
        return character

    def get_characters(self) -> list[models.Character]:
        with self.connection("characters") as conn:
            rows = conn.execute(
                "SELECT id, name, age, gender, description, voice, goals, traits, bio FROM characters ORDER BY name"
            ).fetchall()
        return [
            models.Character(
                id=row["id"],
                name=row["name"],
                age=row["age"],
                gender=row["gender"],
                description=row["description"],
                voice=row["voice"],
                goals=row["goals"],
                traits=row["traits"],
                bio=row["bio"],
            )
            for row in rows
        ]

    def log_chat_history(self, history: models.ChatHistory) -> models.ChatHistory:
        with self.connection("history") as conn:
            cursor = conn.execute(
                """
                INSERT INTO chat_history (user_text, result_text, style_applied, session_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    history.user_text,
                    history.result_text,
                    history.style_applied,
                    history.session_id,
                ),
            )
            history.id = cursor.lastrowid
        return history

    def get_history(self, limit: int = 50) -> list[models.ChatHistory]:
        with self.connection("history") as conn:
            rows = conn.execute(
                "SELECT id, time, user_text, result_text, style_applied, session_id FROM chat_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            models.ChatHistory(
                id=row["id"],
                time=row["time"],
                user_text=row["user_text"],
                result_text=row["result_text"],
                style_applied=row["style_applied"],
                session_id=row["session_id"],
            )
            for row in rows
        ]

    def add_session(self, session: models.RoleplaySession) -> models.RoleplaySession:
        with self.connection("roleplay") as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (character_id, setting, user_goals) VALUES (?, ?, ?)",
                (session.character_id, session.setting, session.user_goals),
            )
            session.id = cursor.lastrowid
        return session

    def add_dialogue(self, dialogue: models.Dialogue) -> models.Dialogue:
        with self.connection("roleplay") as conn:
            cursor = conn.execute(
                "INSERT INTO dialogue (session_id, speaker, message, edited) VALUES (?, ?, ?, ?)",
                (dialogue.session_id, dialogue.speaker, dialogue.message, int(dialogue.edited)),
            )
            dialogue.id = cursor.lastrowid
        return dialogue

    def get_dialogue(self, session_id: int) -> list[models.Dialogue]:
        with self.connection("roleplay") as conn:
            rows = conn.execute(
                "SELECT id, session_id, speaker, message, edited, timestamp FROM dialogue WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
        return [
            models.Dialogue(
                id=row["id"],
                session_id=row["session_id"],
                speaker=row["speaker"],
                message=row["message"],
                edited=bool(row["edited"]),
                timestamp=row["timestamp"],
            )
            for row in rows
        ]

    def set_character_state(self, state: models.CharacterState) -> models.CharacterState:
        with self.connection("roleplay") as conn:
            conn.execute(
                "INSERT INTO character_state (session_id, mood, memory, notes) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(session_id) DO UPDATE SET mood = excluded.mood, memory = excluded.memory, notes = excluded.notes",
                (state.session_id, state.mood, state.memory, state.notes),
            )
        return state

    def get_character_state(self, session_id: int) -> Optional[models.CharacterState]:
        with self.connection("roleplay") as conn:
            row = conn.execute(
                "SELECT session_id, mood, memory, notes FROM character_state WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            return None
        return models.CharacterState(
            session_id=row["session_id"],
            mood=row["mood"],
            memory=row["memory"],
            notes=row["notes"],
        )

    def close(self) -> None:
        for conn in self._connections.values():
            conn.close()
        self._connections.clear()


__all__ = ["DatabaseManager"]
