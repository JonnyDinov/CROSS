from typing import List, Optional, Dict, Any, Tuple

from app.core.database import Database
from app.core.memory import MemoryStore
from app.core.models import (
    Character,
    LoreItem,
    Event,
    Scene,
    SceneMessage,
    Template,
    Quest,
    MemoryRecord,
)


class WorldService:
    def __init__(self, database: Database, memory_store: MemoryStore):
        self.db = database
        self.memory = memory_store

    # Characters
    def list_characters(self) -> List[Character]:
        return self.db.get_all_characters()

    def save_character(self, character: Character) -> int:
        result = self.db.save_character(character)
        self.memory.add_memory(
            record=self.memory_record(
                "semantic",
                character.name,
                {
                    "entity_type": "character",
                    "character_id": result,
                },
                f"{character.name}: {character.description}. Характер: {character.personality}"
            ),
            embed=False,
        )
        return result

    def get_character(self, character_id: int) -> Optional[Character]:
        return self.db.get_character_by_id(character_id)

    def delete_character(self, character_id: int):
        self.db.delete_character(character_id)

    # Lore
    def list_lore(self) -> List[LoreItem]:
        return self.db.get_all_lore()

    def save_lore(self, lore: LoreItem) -> int:
        result = self.db.save_lore(lore)
        self.memory.add_memory(self.memory_record(
            "semantic",
            lore.title,
            {"entity_type": "lore", "category": lore.category},
            lore.summary or lore.details
        ))
        return result

    def delete_lore(self, lore_id: int):
        self.db.delete_lore(lore_id)

    # Events
    def list_events(self) -> List[Event]:
        return self.db.get_all_events()

    def save_event(self, event: Event) -> int:
        result = self.db.save_event(event)
        self.memory.add_memory(self.memory_record(
            "episodic",
            event.title,
            {"entity_type": "event", "event_id": result},
            event.description
        ))
        return result

    def delete_event(self, event_id: int):
        self.db.delete_event(event_id)

    # Scenes
    def list_scenes(self) -> List[Scene]:
        return self.db.get_all_scenes()

    def save_scene(self, scene: Scene) -> int:
        return self.db.save_scene(scene)

    def delete_scene(self, scene_id: int):
        self.db.delete_scene(scene_id)

    def list_scene_messages(self, scene_id: int) -> List[SceneMessage]:
        return self.db.get_scene_messages(scene_id)

    def add_scene_message(self, scene_id: int, speaker: str, content: str, order_index: int, variant: Optional[str] = None) -> int:
        message = SceneMessage(
            id=None,
            scene_id=scene_id,
            order_index=order_index,
            speaker=speaker,
            content=content,
            variant_group=variant,
        )
        message_id = self.db.add_scene_message(message)
        self.memory.add_memory(self.memory_record(
            "episodic",
            f"scene:{scene_id}",
            {"scene_id": scene_id, "speaker": speaker},
            content
        ))
        self.memory.add_to_working_memory(scene_id, {"speaker": speaker, "content": content})
        return message_id

    def update_scene_message(self, message_id: int, content: str):
        self.db.update_scene_message(message_id, content)

    def delete_scene_message(self, message_id: int):
        self.db.delete_scene_message(message_id)

    # Templates
    def list_templates(self) -> List[Template]:
        return self.db.get_all_templates()

    def save_template(self, template: Template) -> int:
        return self.db.save_template(template)

    def delete_template(self, template_id: int):
        self.db.delete_template(template_id)

    # Quests
    def list_quests(self) -> List[Quest]:
        return self.db.get_all_quests()

    def save_quest(self, quest: Quest) -> int:
        return self.db.save_quest(quest)

    def delete_quest(self, quest_id: int):
        self.db.delete_quest(quest_id)

    # Settings
    def get_setting(self, key: str, default: str = "") -> str:
        return self.db.get_setting(key, default)

    def save_setting(self, key: str, value: str):
        self.db.save_setting(key, value)

    @staticmethod
    def memory_record(kind: str, label: str, metadata: Dict[str, Any], content: str):
        return MemoryRecord(id=None, kind=kind, label=label, metadata=metadata, content=content)
