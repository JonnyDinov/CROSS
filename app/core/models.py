from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Character:
    id: Optional[int]
    name: str
    description: str = ""
    personality: str = ""
    speech_style: str = ""
    goals: str = ""
    relationships: str = ""
    faction: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class LoreItem:
    id: Optional[int]
    category: str
    title: str
    summary: str = ""
    details: str = ""
    relations: str = ""


@dataclass
class Event:
    id: Optional[int]
    title: str
    description: str = ""
    location: str = ""
    participants: str = ""
    consequences: str = ""
    status: str = "planned"


@dataclass
class Scene:
    id: Optional[int]
    title: str
    topic: str = ""
    location: str = ""
    participants: List[str] = field(default_factory=list)
    summary: str = ""
    ongoing: bool = True


@dataclass
class SceneMessage:
    id: Optional[int]
    scene_id: int
    order_index: int
    speaker: str
    content: str
    variant_group: Optional[str] = None


@dataclass
class Template:
    id: Optional[int]
    name: str
    template_type: str
    content: str


@dataclass
class Quest:
    id: Optional[int]
    title: str
    quest_type: str
    description: str
    rewards: str = ""
    prerequisites: str = ""


@dataclass
class MemoryRecord:
    id: Optional[int]
    kind: str
    label: str
    metadata: Dict[str, Any]
    content: str
    embedding: Optional[List[float]] = None


@dataclass
class ExportResult:
    path: str
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)
