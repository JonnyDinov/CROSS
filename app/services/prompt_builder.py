from typing import List, Dict, Any

from app.core.database import Database
from app.core.memory import MemoryStore


class PromptBuilder:
    def __init__(self, db: Database, memory_store: MemoryStore):
        self.db = db
        self.memory_store = memory_store

    def build_character_prompt(self, character_id: int, scene_id: int = None) -> str:
        character = self.db.get_character_by_id(character_id)
        if not character:
            return ""

        prompt_sections = [
            "Ты помогаешь авторам ролевого мира. Используй следующие данные:",
            f"Имя: {character.name}",
            f"Описание: {character.description}",
            f"Характер: {character.personality}",
            f"Манера речи: {character.speech_style}",
            f"Цели: {character.goals}",
            f"Связи: {character.relationships}",
        ]

        semantic_memories = self.memory_store.get_semantic_facts(character.name)
        if semantic_memories:
            prompt_sections.append("Факты семантической памяти:")
            for fact in semantic_memories[:10]:
                prompt_sections.append(f"- {fact.content}")

        if scene_id:
            episodic = self.memory_store.search_episodic(f"{character.name} сцена {scene_id}")
            if episodic:
                prompt_sections.append("Воспоминания прошлых событий:")
                for memory in episodic:
                    prompt_sections.append(f"- {memory.content}")

            working_memory = self.memory_store.get_working_memory(scene_id)
            if working_memory:
                prompt_sections.append("Последние реплики сцены:")
                for entry in working_memory[-5:]:
                    prompt_sections.append(f"{entry['speaker']}: {entry['content']}")

        return "\n".join(section for section in prompt_sections if section.strip())

    def build_scene_context(self, scene_id: int) -> str:
        scene = next((s for s in self.db.get_all_scenes() if s.id == scene_id), None)
        if not scene:
            return ""

        prompt_sections = [
            "Генерация сцен в ролевом мире.",
            f"Сцена: {scene.title}",
            f"Тематика: {scene.topic}",
            f"Локация: {scene.location}",
            f"Участники: {', '.join(scene.participants)}",
            f"Сводка: {scene.summary}",
        ]

        semantic = []
        for participant in scene.participants:
            semantic.extend(self.memory_store.get_semantic_facts(participant, limit=5))

        if semantic:
            prompt_sections.append("Семантическая память участников:")
            for fact in semantic[:10]:
                prompt_sections.append(f"- {fact.label}: {fact.content}")

        episodic = self.memory_store.search_episodic(scene.title)
        if episodic:
            prompt_sections.append("Похожие эпизоды из памяти:")
            for memory in episodic[:5]:
                prompt_sections.append(f"- {memory.content}")

        working_memory = self.memory_store.get_working_memory(scene_id)
        if working_memory:
            prompt_sections.append("Последние реплики:")
            for entry in working_memory[-6:]:
                prompt_sections.append(f"{entry['speaker']}: {entry['content']}")

        return "\n".join(section for section in prompt_sections if section.strip())
