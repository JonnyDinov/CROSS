from __future__ import annotations

from typing import Iterable, Sequence

from ai_helper import models


def build_style_prompt(style_name: str, age: str | None, yaml_rules: str, user_text: str, extra_context: str = "") -> tuple[str, str]:
    system_prompt_lines = [f"Ты — редактор текста. Перепиши данное сообщение в стиле \"{style_name}\"."]
    if age:
        system_prompt_lines.append(f"Возраст автора: {age}.")
    if yaml_rules.strip():
        system_prompt_lines.append(f"Требования: {yaml_rules.strip()}")
    if extra_context.strip():
        system_prompt_lines.append(f"Дополнительный контекст: {extra_context.strip()}")
    system_prompt_lines.append("Сохрани смысл, имена собственные и структуру.")
    system_prompt = "\n".join(system_prompt_lines)
    return system_prompt, user_text


def build_roleplay_prompt(
    character: models.Character,
    session_state: models.CharacterState | None,
    setting: str,
    dialogue_history: Sequence[models.Dialogue],
) -> tuple[str, list[dict[str, str]]]:
    system_lines = [
        "Ты — персонаж в ролевой игре.",
        f"Имя: {character.name}",
    ]
    if character.age:
        system_lines.append(f"Возраст: {character.age}")
    if character.traits:
        system_lines.append(f"Черты: {character.traits}")
    if character.voice:
        system_lines.append(f"Голос и стиль: {character.voice}")
    if character.goals:
        system_lines.append(f"Цели: {character.goals}")
    if session_state:
        if session_state.mood:
            system_lines.append(f"Текущее настроение: {session_state.mood}")
        if session_state.memory:
            system_lines.append(f"Важные воспоминания: {session_state.memory}")
        if session_state.notes:
            system_lines.append(f"Заметки: {session_state.notes}")
    if setting:
        system_lines.append(f"Контекст: {setting}")

    system_lines.append("Отвечай как персонаж, сохраняя характер, голос и цели.")
    system_prompt = "\n".join(system_lines)

    history_messages: list[dict[str, str]] = []
    for dialogue in dialogue_history:
        speaker_role = dialogue.speaker.lower()
        role = "assistant" if speaker_role not in {"user", "player"} else "user"
        history_messages.append({"role": role, "content": dialogue.message})

    return system_prompt, history_messages


def build_quest_prompt(
    quest_style: str,
    genre: str,
    difficulty: str,
    characters: Iterable[models.Character],
    synopsis: str,
) -> tuple[str, str]:
    system_lines = [f"Сгенерируй квест в стиле \"{quest_style}\"."]
    if genre:
        system_lines.append(f"Жанр: {genre}.")
    if difficulty:
        system_lines.append(f"Сложность: {difficulty}.")

    formatted_characters = []
    for character in characters:
        parts = [character.name or "Безымянный герой"]
        if character.traits:
            parts.append(f"черты: {character.traits}")
        if character.goals:
            parts.append(f"цели: {character.goals}")
        formatted_characters.append("; ".join(parts))

    if formatted_characters:
        system_lines.append("Используй персонажей: " + ", ".join(formatted_characters) + ".")

    system_lines.append(
        "Формат Markdown:\n- Заголовок\n- Краткая суть\n- Персонажи (имя, роль, характер)\n- Цели игрока поэтапно\n- Диалоги\n- Возможные варианты/развязки\n- Награды"
    )
    system_prompt = "\n".join(system_lines)
    user_prompt = synopsis or ""
    return system_prompt, user_prompt


def build_book_partition_prompt(
    style_name: str,
    parameters: dict[str, str],
    content: str,
) -> tuple[str, str]:
    system_lines = [
        "Ты — литературный редактор и верстальщик.",
        f"Стиль оформления: {style_name}.",
    ]
    for key, value in parameters.items():
        if value:
            system_lines.append(f"{key}: {value}")
    system_lines.append("Разбей текст на главы и страницы по лимиту символов.")
    system_prompt = "\n".join(system_lines)
    return system_prompt, content
