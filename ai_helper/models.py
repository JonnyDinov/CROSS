from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Character:
    id: Optional[int] = None
    name: str = ""
    age: Optional[int] = None
    gender: str = ""
    description: str = ""
    voice: str = ""
    goals: str = ""
    traits: str = ""
    bio: str = ""


@dataclass
class Relationship:
    id: Optional[int] = None
    character_id: int = 0
    target_id: int = 0
    relation: str = ""
    notes: str = ""


@dataclass
class Style:
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    yaml_rules: str = ""
    active: bool = True


@dataclass
class Quest:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    genre: str = ""
    characters: str = ""
    difficulty: str = ""
    rewards: str = ""
    json: str = ""


@dataclass
class Book:
    id: Optional[int] = None
    title: str = ""
    author: str = ""
    chars_per_page: int = 2000
    created_at: Optional[datetime] = None


@dataclass
class Page:
    id: Optional[int] = None
    book_id: int = 0
    page_number: int = 0
    content: str = ""


@dataclass
class RoleplaySession:
    id: Optional[int] = None
    character_id: int = 0
    setting: str = ""
    start_time: Optional[datetime] = None
    user_goals: str = ""


@dataclass
class Dialogue:
    id: Optional[int] = None
    session_id: int = 0
    speaker: str = ""
    message: str = ""
    edited: bool = False
    timestamp: Optional[datetime] = None


@dataclass
class CharacterState:
    session_id: int = 0
    mood: str = ""
    memory: str = ""
    notes: str = ""


@dataclass
class ChatHistory:
    id: Optional[int] = None
    time: Optional[datetime] = None
    user_text: str = ""
    result_text: str = ""
    style_applied: str = ""
    session_id: Optional[int] = None
