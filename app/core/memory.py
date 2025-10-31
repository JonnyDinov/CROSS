import json
import os
import sqlite3
from typing import List, Dict, Any, Optional

import numpy as np

from app.core.models import MemoryRecord
from app.core.ollama import OllamaClient


class MemoryStore:
    """Combined episodic, semantic, and working memory manager."""

    def __init__(self, db_path: str, ollama_client: OllamaClient):
        self.db_path = db_path
        self.ollama_client = ollama_client
        self._ensure_tables()
        self._working_memory: Dict[int, List[Dict[str, Any]]] = {}

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kind TEXT NOT NULL,
                label TEXT,
                metadata TEXT,
                content TEXT NOT NULL,
                embedding BLOB
            )
            """
        )
        conn.commit()
        conn.close()

    def add_memory(self, record: MemoryRecord, embed: bool = True) -> int:
        embedding = None
        if embed and record.content:
            embedding = self.ollama_client.embed_text(record.content)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO memory (kind, label, metadata, content, embedding)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.kind,
                record.label,
                json.dumps(record.metadata or {}),
                record.content,
                json.dumps(embedding) if embedding else None,
            ),
        )
        conn.commit()
        record_id = cursor.lastrowid
        conn.close()
        return record_id

    def search_episodic(self, query: str, top_k: int = 5) -> List[MemoryRecord]:
        query_embedding = self.ollama_client.embed_text(query)
        if not query_embedding:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, kind, label, metadata, content, embedding FROM memory WHERE embedding IS NOT NULL"
        )
        rows = cursor.fetchall()
        conn.close()

        docs = []
        for row in rows:
            embedding = json.loads(row[5]) if row[5] else None
            if not embedding:
                continue
            similarity = self._cosine_similarity(query_embedding, embedding)
            docs.append(
                (
                    similarity,
                    MemoryRecord(
                        id=row[0],
                        kind=row[1],
                        label=row[2],
                        metadata=json.loads(row[3]) if row[3] else {},
                        content=row[4],
                        embedding=embedding,
                    ),
                )
            )
        docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in docs[:top_k]]

    def get_semantic_facts(self, entity: str, limit: int = 20) -> List[MemoryRecord]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, kind, label, metadata, content FROM memory
            WHERE kind = 'semantic' AND (label = ? OR metadata LIKE ?)
            ORDER BY id DESC LIMIT ?
            """,
            (entity, f'%"{entity}"%', limit),
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            MemoryRecord(
                id=row[0],
                kind=row[1],
                label=row[2],
                metadata=json.loads(row[3]) if row[3] else {},
                content=row[4],
            )
            for row in rows
        ]

    def add_to_working_memory(self, scene_id: int, message: Dict[str, Any], max_messages: int = 10):
        history = self._working_memory.setdefault(scene_id, [])
        history.append(message)
        if len(history) > max_messages:
            history.pop(0)

    def set_working_memory(self, scene_id: int, messages: List[Dict[str, Any]]):
        self._working_memory[scene_id] = messages[-10:] if len(messages) > 10 else messages

    def get_working_memory(self, scene_id: int) -> List[Dict[str, Any]]:
        return list(self._working_memory.get(scene_id, []))

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
