from __future__ import annotations

import atexit
import json
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable, List, Optional


class DatabaseManager:
    """Singleton-style helper around SQLite access for the application."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        self.db_path = Path(db_path or "data/dinov_ai.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._initialize_schema()
        atexit.register(self.close)

    @property
    def connection(self) -> sqlite3.Connection:
        return self._connection

    def close(self) -> None:
        with self._lock:
            if self._connection:
                self._connection.commit()
                self._connection.close()
                self._connection = None  # type: ignore[assignment]

    def _initialize_schema(self) -> None:
        create_statements = [
            """
            CREATE TABLE IF NOT EXISTS lore (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                content TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                personality TEXT,
                speech_style TEXT,
                backstory TEXT,
                world_role TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                theme TEXT,
                narrative_style TEXT,
                involved_characters TEXT,
                content TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS dialogues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER,
                player_line TEXT,
                ai_response TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(character_id) REFERENCES characters(id) ON DELETE SET NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """,
        ]

        with self._lock:
            cursor = self._connection.cursor()
            for statement in create_statements:
                cursor.execute(statement)

            cursor.execute("""
                INSERT OR IGNORE INTO lore (id, content) VALUES (1, ?)
            """, (
                "Добро пожаловать в мир средневекового фэнтези. Здесь правят короли и маги, а драконы всё ещё оставляют след в судьбах людей.",
            ))

            default_settings = {
                "ollama_url": "http://localhost:11434",
                "model": "llama2",
                "global_style": "Псевдосредневековый стиль с высокопарной речью.",
                "save_dialogue_context": json.dumps(True),
            }
            for key, value in default_settings.items():
                cursor.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    (key, str(value)),
                )

            self._connection.commit()

    def execute(
        self, query: str, params: Iterable[Any] = (), commit: bool = False
    ) -> sqlite3.Cursor:
        with self._lock:
            cursor = self._connection.cursor()
            cursor.execute(query, tuple(params))
            if commit:
                self._connection.commit()
            return cursor

    def fetchone(
        self, query: str, params: Iterable[Any] = ()
    ) -> Optional[sqlite3.Row]:
        return self.execute(query, params).fetchone()

    def fetchall(
        self, query: str, params: Iterable[Any] = ()
    ) -> List[sqlite3.Row]:
        return self.execute(query, params).fetchall()


db = DatabaseManager()
