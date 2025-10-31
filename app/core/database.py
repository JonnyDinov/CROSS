import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from app.core.models import (
    Character, LoreItem, Event, Scene, SceneMessage, Template, Quest
)


class Database:
    def __init__(self, db_path: str = "world.db"):
        self.db_path = db_path
        self._init_database()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_database(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS characters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    personality TEXT,
                    speech_style TEXT,
                    goals TEXT,
                    relationships TEXT,
                    faction TEXT,
                    tags TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS lore (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    summary TEXT,
                    details TEXT,
                    relations TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    location TEXT,
                    participants TEXT,
                    consequences TEXT,
                    status TEXT DEFAULT 'planned'
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scenes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    topic TEXT,
                    location TEXT,
                    participants TEXT,
                    summary TEXT,
                    ongoing INTEGER DEFAULT 1
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scene_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scene_id INTEGER NOT NULL,
                    order_index INTEGER NOT NULL,
                    speaker TEXT NOT NULL,
                    content TEXT NOT NULL,
                    variant_group TEXT,
                    FOREIGN KEY (scene_id) REFERENCES scenes(id) ON DELETE CASCADE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    template_type TEXT NOT NULL,
                    content TEXT NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS quests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    quest_type TEXT,
                    description TEXT,
                    rewards TEXT,
                    prerequisites TEXT
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def save_character(self, character: Character) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            tags_str = json.dumps(character.tags)
            
            if character.id is None:
                cursor.execute("""
                    INSERT INTO characters 
                    (name, description, personality, speech_style, goals, relationships, faction, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (character.name, character.description, character.personality,
                      character.speech_style, character.goals, character.relationships,
                      character.faction, tags_str))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE characters 
                    SET name=?, description=?, personality=?, speech_style=?, 
                        goals=?, relationships=?, faction=?, tags=?
                    WHERE id=?
                """, (character.name, character.description, character.personality,
                      character.speech_style, character.goals, character.relationships,
                      character.faction, tags_str, character.id))
                return character.id

    def get_all_characters(self) -> List[Character]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM characters ORDER BY name")
            rows = cursor.fetchall()
            
            characters = []
            for row in rows:
                tags = json.loads(row['tags']) if row['tags'] else []
                characters.append(Character(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or "",
                    personality=row['personality'] or "",
                    speech_style=row['speech_style'] or "",
                    goals=row['goals'] or "",
                    relationships=row['relationships'] or "",
                    faction=row['faction'] or "",
                    tags=tags
                ))
            return characters

    def get_character_by_id(self, character_id: int) -> Optional[Character]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM characters WHERE id=?", (character_id,))
            row = cursor.fetchone()
            
            if row:
                tags = json.loads(row['tags']) if row['tags'] else []
                return Character(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or "",
                    personality=row['personality'] or "",
                    speech_style=row['speech_style'] or "",
                    goals=row['goals'] or "",
                    relationships=row['relationships'] or "",
                    faction=row['faction'] or "",
                    tags=tags
                )
            return None

    def delete_character(self, character_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM characters WHERE id=?", (character_id,))

    def save_lore(self, lore: LoreItem) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if lore.id is None:
                cursor.execute("""
                    INSERT INTO lore (category, title, summary, details, relations)
                    VALUES (?, ?, ?, ?, ?)
                """, (lore.category, lore.title, lore.summary, lore.details, lore.relations))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE lore 
                    SET category=?, title=?, summary=?, details=?, relations=?
                    WHERE id=?
                """, (lore.category, lore.title, lore.summary, lore.details, lore.relations, lore.id))
                return lore.id

    def get_all_lore(self) -> List[LoreItem]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM lore ORDER BY category, title")
            rows = cursor.fetchall()
            
            return [LoreItem(
                id=row['id'],
                category=row['category'],
                title=row['title'],
                summary=row['summary'] or "",
                details=row['details'] or "",
                relations=row['relations'] or ""
            ) for row in rows]

    def delete_lore(self, lore_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM lore WHERE id=?", (lore_id,))

    def save_event(self, event: Event) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if event.id is None:
                cursor.execute("""
                    INSERT INTO events (title, description, location, participants, consequences, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (event.title, event.description, event.location, 
                      event.participants, event.consequences, event.status))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE events 
                    SET title=?, description=?, location=?, participants=?, consequences=?, status=?
                    WHERE id=?
                """, (event.title, event.description, event.location, 
                      event.participants, event.consequences, event.status, event.id))
                return event.id

    def get_all_events(self) -> List[Event]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY title")
            rows = cursor.fetchall()
            
            return [Event(
                id=row['id'],
                title=row['title'],
                description=row['description'] or "",
                location=row['location'] or "",
                participants=row['participants'] or "",
                consequences=row['consequences'] or "",
                status=row['status']
            ) for row in rows]

    def delete_event(self, event_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events WHERE id=?", (event_id,))

    def save_scene(self, scene: Scene) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            participants_str = json.dumps(scene.participants)
            
            if scene.id is None:
                cursor.execute("""
                    INSERT INTO scenes (title, topic, location, participants, summary, ongoing)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (scene.title, scene.topic, scene.location, participants_str, 
                      scene.summary, 1 if scene.ongoing else 0))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE scenes 
                    SET title=?, topic=?, location=?, participants=?, summary=?, ongoing=?
                    WHERE id=?
                """, (scene.title, scene.topic, scene.location, participants_str, 
                      scene.summary, 1 if scene.ongoing else 0, scene.id))
                return scene.id

    def get_all_scenes(self) -> List[Scene]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM scenes ORDER BY id DESC")
            rows = cursor.fetchall()
            
            scenes = []
            for row in rows:
                participants = json.loads(row['participants']) if row['participants'] else []
                scenes.append(Scene(
                    id=row['id'],
                    title=row['title'],
                    topic=row['topic'] or "",
                    location=row['location'] or "",
                    participants=participants,
                    summary=row['summary'] or "",
                    ongoing=bool(row['ongoing'])
                ))
            return scenes

    def delete_scene(self, scene_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scene_messages WHERE scene_id=?", (scene_id,))
            cursor.execute("DELETE FROM scenes WHERE id=?", (scene_id,))

    def add_scene_message(self, message: SceneMessage) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scene_messages (scene_id, order_index, speaker, content, variant_group)
                VALUES (?, ?, ?, ?, ?)
            """, (message.scene_id, message.order_index, message.speaker, 
                  message.content, message.variant_group))
            return cursor.lastrowid

    def get_scene_messages(self, scene_id: int) -> List[SceneMessage]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM scene_messages 
                WHERE scene_id=? AND variant_group IS NULL
                ORDER BY order_index
            """, (scene_id,))
            rows = cursor.fetchall()
            
            return [SceneMessage(
                id=row['id'],
                scene_id=row['scene_id'],
                order_index=row['order_index'],
                speaker=row['speaker'],
                content=row['content'],
                variant_group=row['variant_group']
            ) for row in rows]

    def update_scene_message(self, message_id: int, content: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE scene_messages SET content=? WHERE id=?", (content, message_id))

    def delete_scene_message(self, message_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM scene_messages WHERE id=?", (message_id,))

    def save_template(self, template: Template) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if template.id is None:
                cursor.execute("""
                    INSERT INTO templates (name, template_type, content)
                    VALUES (?, ?, ?)
                """, (template.name, template.template_type, template.content))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE templates SET name=?, template_type=?, content=? WHERE id=?
                """, (template.name, template.template_type, template.content, template.id))
                return template.id

    def get_all_templates(self) -> List[Template]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM templates ORDER BY name")
            rows = cursor.fetchall()
            
            return [Template(
                id=row['id'],
                name=row['name'],
                template_type=row['template_type'],
                content=row['content']
            ) for row in rows]

    def delete_template(self, template_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM templates WHERE id=?", (template_id,))

    def save_quest(self, quest: Quest) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if quest.id is None:
                cursor.execute("""
                    INSERT INTO quests (title, quest_type, description, rewards, prerequisites)
                    VALUES (?, ?, ?, ?, ?)
                """, (quest.title, quest.quest_type, quest.description, quest.rewards, quest.prerequisites))
                return cursor.lastrowid
            else:
                cursor.execute("""
                    UPDATE quests SET title=?, quest_type=?, description=?, rewards=?, prerequisites=?
                    WHERE id=?
                """, (quest.title, quest.quest_type, quest.description, 
                      quest.rewards, quest.prerequisites, quest.id))
                return quest.id

    def get_all_quests(self) -> List[Quest]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM quests ORDER BY title")
            rows = cursor.fetchall()
            
            return [Quest(
                id=row['id'],
                title=row['title'],
                quest_type=row['quest_type'] or "",
                description=row['description'] or "",
                rewards=row['rewards'] or "",
                prerequisites=row['prerequisites'] or ""
            ) for row in rows]

    def delete_quest(self, quest_id: int):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM quests WHERE id=?", (quest_id,))

    def get_setting(self, key: str, default: str = "") -> str:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else default

    def save_setting(self, key: str, value: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
            """, (key, value))

    def export_world(self) -> Dict[str, Any]:
        return {
            'characters': [vars(c) for c in self.get_all_characters()],
            'lore': [vars(l) for l in self.get_all_lore()],
            'events': [vars(e) for e in self.get_all_events()],
            'scenes': [vars(s) for s in self.get_all_scenes()],
            'templates': [vars(t) for t in self.get_all_templates()],
            'quests': [vars(q) for q in self.get_all_quests()],
        }

    def import_world(self, data: Dict[str, Any]):
        if 'characters' in data:
            for char_data in data['characters']:
                char_data['id'] = None
                self.save_character(Character(**char_data))
        
        if 'lore' in data:
            for lore_data in data['lore']:
                lore_data['id'] = None
                self.save_lore(LoreItem(**lore_data))
        
        if 'events' in data:
            for event_data in data['events']:
                event_data['id'] = None
                self.save_event(Event(**event_data))
        
        if 'templates' in data:
            for template_data in data['templates']:
                template_data['id'] = None
                self.save_template(Template(**template_data))
        
        if 'quests' in data:
            for quest_data in data['quests']:
                quest_data['id'] = None
                self.save_quest(Quest(**quest_data))
