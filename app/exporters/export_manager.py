import os
import json
from datetime import datetime
from typing import List

from app.core.database import Database
from app.core.models import Scene, Character


class ExportManager:
    def __init__(self, db: Database):
        self.db = db

    def export_world_json(self, path: str):
        data = self.db.export_world()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_world_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.db.import_world(data)

    def export_scene_markdown(self, scene: Scene, messages: List[tuple], path: str):
        lines = [
            f"# {scene.title}",
            "",
            f"**Тема:** {scene.topic}",
            f"**Локация:** {scene.location}",
            f"**Участники:** {', '.join(scene.participants)}",
            "",
            "---",
            "",
        ]

        for speaker, content in messages:
            lines.append(f"**{speaker}:** {content}")
            lines.append("")

        lines.append("---")
        lines.append(f"Экспорт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def export_character_markdown(self, character: Character, path: str):
        lines = [
            f"# {character.name}",
            "",
            f"**Фракция:** {character.faction}",
            "",
            "## Описание",
            "",
            character.description,
            "",
            "## Характер",
            "",
            character.personality,
            "",
            "## Манера речи",
            "",
            character.speech_style,
            "",
            "## Цели",
            "",
            character.goals,
            "",
            "## Связи",
            "",
            character.relationships,
            "",
            "---",
            f"Экспорт: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
