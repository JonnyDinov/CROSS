from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Iterable, List

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from ai_helper.config import APP_NAME
from ai_helper.models import (
    Character,
    CharacterState,
    ChatHistory,
    Dialogue,
    RoleplaySession,
    Style,
)
from ai_helper.services import GlobalHotkeyListener, HotkeyCallbacks, OllamaClient
from ai_helper.services import prompts
from ai_helper.storage import DatabaseManager


class QuickEditorView(Static):
    def compose(self) -> ComposeResult:
        yield Label("Стиль")
        self.style_input = Input(id="input-style", placeholder="средневековый, деловой...")
        yield self.style_input

        yield Label("Возраст автора")
        self.age_input = Input(id="input-age", placeholder="например, 17")
        yield self.age_input

        yield Label("Дополнительный контекст")
        self.context_input = Input(id="input-context", placeholder="Где используется текст")
        yield self.context_input

        yield Label("Текст для преобразования")
        self.source_text = TextArea(id="source-text", soft_wrap=True)
        yield self.source_text

        yield Button("Переписать текст (Alt+W)", id="run-transform")

        yield Label("Результат")
        self.result_area = TextArea(id="result-area", soft_wrap=True, read_only=True)
        yield self.result_area

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-transform":
            await self.run_transformation()

    async def run_transformation(self) -> None:
        style_name = (self.style_input.value or "").strip()
        age = (self.age_input.value or "").strip()
        context = (self.context_input.value or "").strip()
        source = (self.source_text.value or "").strip()
        if not source:
            self.result_area.value = "Введите текст для преобразования."
            return

        styles = self.app.database.get_styles()  # type: ignore[attr-defined]
        style_rules = next(
            (style.yaml_rules for style in styles if style.name.lower() == style_name.lower()),
            "",
        )
        system_prompt, user_prompt = prompts.build_style_prompt(
            style_name or "универсальный",
            age,
            style_rules,
            source,
            context,
        )
        self.result_area.value = "Ожидание ответа от модели..."
        response = await self.app.call_ollama(system_prompt, user_prompt)  # type: ignore[attr-defined]
        response_text = response or "Модель не вернула ответа."
        self.result_area.value = response_text

        self.app.database.log_chat_history(  # type: ignore[attr-defined]
            ChatHistory(user_text=source, result_text=response_text, style_applied=style_name or "универсальный")
        )
        self.app.refresh_history_panels()  # type: ignore[attr-defined]


class StyleManagerView(Static):
    def compose(self) -> ComposeResult:
        yield Label("Стили написания")
        self.styles_list = ListView(id="style-list")
        yield self.styles_list

        yield Label("Название")
        self.name_input = Input(id="style-name")
        yield self.name_input

        yield Label("Описание")
        self.description_input = TextArea(id="style-description", soft_wrap=True)
        yield self.description_input

        yield Label("YAML правила")
        self.rules_input = TextArea(id="style-rules", soft_wrap=True)
        yield self.rules_input

        yield Button("Сохранить стиль", id="save-style")

    def on_mount(self) -> None:
        self.refresh_styles()

    def refresh_styles(self) -> None:
        self.styles_list.clear()
        for style in self.app.database.get_styles():  # type: ignore[attr-defined]
            description = f" — {style.description}" if style.description else ""
            self.styles_list.append(ListItem(Label(f"{style.name}{description}")))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "save-style":
            return

        name = (self.name_input.value or "").strip()
        if not name:
            self.app.bell()  # type: ignore[attr-defined]
            return
        description = (self.description_input.value or "").strip()
        rules = (self.rules_input.value or "").strip()

        self.app.database.add_style(  # type: ignore[attr-defined]
            Style(name=name, description=description, yaml_rules=rules, active=True)
        )
        self.name_input.value = ""
        self.description_input.value = ""
        self.rules_input.value = ""
        self.refresh_styles()


class CharacterManagerView(Static):
    def compose(self) -> ComposeResult:
        yield Label("Персонажи")
        self.characters_list = ListView(id="characters-list")
        yield self.characters_list

        yield Label("Имя")
        self.name_input = Input(id="character-name")
        yield self.name_input

        yield Label("Возраст")
        self.age_input = Input(id="character-age")
        yield self.age_input

        yield Label("Пол")
        self.gender_input = Input(id="character-gender")
        yield self.gender_input

        yield Label("Черты и описание")
        self.traits_input = TextArea(id="character-traits", soft_wrap=True)
        yield self.traits_input

        yield Label("Голос и стиль")
        self.voice_input = Input(id="character-voice")
        yield self.voice_input

        yield Label("Цели")
        self.goals_input = TextArea(id="character-goals", soft_wrap=True)
        yield self.goals_input

        yield Button("Сохранить персонажа", id="save-character")

    def on_mount(self) -> None:
        self.refresh_characters()

    def refresh_characters(self) -> None:
        self.characters_list.clear()
        for character in self.app.database.get_characters():  # type: ignore[attr-defined]
            subtitle = f" — {character.traits}" if character.traits else ""
            self.characters_list.append(ListItem(Label(f"{character.name}{subtitle}")))

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "save-character":
            return

        name = (self.name_input.value or "").strip()
        if not name:
            self.app.bell()  # type: ignore[attr-defined]
            return

        age_value = (self.age_input.value or "").strip()
        age = int(age_value) if age_value.isdigit() else None

        character = Character(
            name=name,
            age=age,
            gender=(self.gender_input.value or "").strip(),
            description=(self.traits_input.value or "").strip(),
            voice=(self.voice_input.value or "").strip(),
            goals=(self.goals_input.value or "").strip(),
            traits=(self.traits_input.value or "").strip(),
            bio="",
        )
        self.app.database.add_character(character)  # type: ignore[attr-defined]
        self.refresh_characters()

        self.name_input.value = ""
        self.age_input.value = ""
        self.gender_input.value = ""
        self.voice_input.value = ""
        self.traits_input.value = ""
        self.goals_input.value = ""


class QuestGeneratorView(Static):
    def compose(self) -> ComposeResult:
        yield Label("Генератор квестов")
        self.style_input = Input(id="quest-style", placeholder="Стиль")
        yield self.style_input
        self.genre_input = Input(id="quest-genre", placeholder="Жанр")
        yield self.genre_input
        self.difficulty_input = Input(id="quest-difficulty", placeholder="Сложность")
        yield self.difficulty_input

        yield Label("Синопсис")
        self.synopsis_input = TextArea(id="quest-synopsis", soft_wrap=True)
        yield self.synopsis_input

        yield Button("Сгенерировать", id="generate-quest")

        yield Label("Результат")
        self.output_area = TextArea(id="quest-output", soft_wrap=True, read_only=True)
        yield self.output_area

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "generate-quest":
            return

        characters = self.app.database.get_characters()  # type: ignore[attr-defined]
        system_prompt, user_prompt = prompts.build_quest_prompt(
            self.style_input.value or "",
            self.genre_input.value or "",
            self.difficulty_input.value or "",
            characters,
            self.synopsis_input.value or "",
        )
        self.output_area.value = "Запрос к модели..."
        response = await self.app.call_ollama(system_prompt, user_prompt)  # type: ignore[attr-defined]
        self.output_area.value = response or "Модель не вернула ответа."


class RoleplayView(Static):
    current_session: RoleplaySession | None = None

    def compose(self) -> ComposeResult:
        yield Label("Ролевая игра")
        self.character_input = Input(id="rp-character", placeholder="Имя персонажа")
        yield self.character_input
        self.setting_input = TextArea(id="rp-setting", soft_wrap=True)
        yield Label("Сеттинг")
        yield self.setting_input
        yield Label("Память персонажа")
        self.memory_input = TextArea(id="rp-memory", soft_wrap=True)
        yield self.memory_input
        yield Label("Настроение")
        self.mood_input = Input(id="rp-mood")
        yield self.mood_input
        yield Label("Цели игрока")
        self.goals_input = TextArea(id="rp-goals", soft_wrap=True)
        yield self.goals_input
        yield Label("Диалог")
        self.dialogue_area = TextArea(id="rp-dialogue", soft_wrap=True, read_only=True)
        yield self.dialogue_area
        yield Label("Ваше сообщение")
        self.message_input = TextArea(id="rp-message", soft_wrap=True)
        yield self.message_input
        yield Button("Отправить", id="rp-send")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "rp-send":
            await self.send_message()

    def _ensure_character(self, name: str) -> Character:
        characters = self.app.database.get_characters()  # type: ignore[attr-defined]
        existing = next((c for c in characters if c.name.lower() == name.lower()), None)
        if existing:
            return existing
        return self.app.database.add_character(Character(name=name))  # type: ignore[attr-defined]

    def _ensure_session(self, character: Character) -> RoleplaySession:
        if self.current_session and self.current_session.character_id == (character.id or 0):
            return self.current_session
        session = self.app.database.add_session(  # type: ignore[attr-defined]
            RoleplaySession(
                character_id=character.id or 0,
                setting=self.setting_input.value or "",
                user_goals=self.goals_input.value or "",
            )
        )
        self.current_session = session
        return session

    def _format_dialogue(self, dialogues: Iterable[Dialogue]) -> str:
        lines: List[str] = []
        for item in dialogues:
            speaker = item.speaker or "NPC"
            if speaker.lower() in {"user", "player"}:
                speaker = "Вы"
            lines.append(f"[{speaker}]: {item.message}")
        return "\n".join(lines)

    async def send_message(self) -> None:
        name = (self.character_input.value or "").strip()
        message_text = (self.message_input.value or "").strip()
        if not name or not message_text:
            self.app.bell()  # type: ignore[attr-defined]
            return

        character = self._ensure_character(name)
        session = self._ensure_session(character)

        state = CharacterState(
            session_id=session.id or 0,
            mood=self.mood_input.value or "",
            memory=self.memory_input.value or "",
            notes="",
        )
        self.app.database.set_character_state(state)  # type: ignore[attr-defined]

        user_dialogue = Dialogue(
            session_id=session.id or 0,
            speaker="user",
            message=message_text,
            edited=False,
        )
        self.app.database.add_dialogue(user_dialogue)  # type: ignore[attr-defined]
        history = self.app.database.get_dialogue(session.id or 0)  # type: ignore[attr-defined]
        system_prompt, messages = prompts.build_roleplay_prompt(
            character,
            state,
            self.setting_input.value or "",
            history,
        )
        self.dialogue_area.value = self._format_dialogue(history) + "\n(Ожидание ответа...)"
        response = await self.app.call_ollama_with_messages(system_prompt, messages)  # type: ignore[attr-defined]
        assistant_dialogue = Dialogue(
            session_id=session.id or 0,
            speaker=character.name or "NPC",
            message=response,
            edited=False,
        )
        self.app.database.add_dialogue(assistant_dialogue)  # type: ignore[attr-defined]
        updated_history = history + [assistant_dialogue]
        self.dialogue_area.value = self._format_dialogue(updated_history)
        self.message_input.value = ""


class HistoryView(Static):
    def compose(self) -> ComposeResult:
        yield Label("История запросов")
        self.history_area = TextArea(id="history-area", soft_wrap=True, read_only=True)
        yield self.history_area

    def on_mount(self) -> None:
        self.refresh_history()

    def refresh_history(self) -> None:
        entries = self.app.database.get_history(limit=50)  # type: ignore[attr-defined]
        lines: List[str] = []
        for entry in entries:
            timestamp = entry.time or ""
            lines.append(
                f"[{timestamp}] Стиль: {entry.style_applied or '—'}\n"
                f"Исходный текст: {entry.user_text}\n"
                f"Результат: {entry.result_text}\n"
                "------------------------------"
            )
        self.history_area.value = "\n".join(lines)


class AIHelperApp(App):
    CSS_PATH = Path(__file__).with_name("styles.tcss")
    TITLE = APP_NAME

    BINDINGS = [
        ("ctrl+c", "quit", "Выход"),
        ("alt+w", "open_quick_editor", "Быстрый редактор"),
        ("alt+f", "open_main_menu", "Главное меню"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.database = DatabaseManager()
        self.ollama = OllamaClient()
        self.hotkeys = GlobalHotkeyListener(
            HotkeyCallbacks(
                quick_editor=self.open_quick_editor,
                main_menu=self.open_main_menu,
            )
        )

    async def on_mount(self) -> None:
        self.hotkeys.start()

    async def on_shutdown(self) -> None:
        self.hotkeys.stop()
        self.database.close()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, id="header")
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("AI Helper", id="app-title")
                yield Button("Главное меню", id="btn-menu")
                yield Button("Редактор текста", id="btn-quick")
                yield Button("Стили", id="btn-styles")
                yield Button("Персонажи", id="btn-characters")
                yield Button("Квесты", id="btn-quests")
                yield Button("Ролевая", id="btn-roleplay")
                yield Button("История", id="btn-history")
            with Container(id="content-panel"):
                with TabbedContent(id="tabs"):
                    with TabPane("Главное меню", id="tab-menu"):
                        yield Label("Добро пожаловать в AI Helper!", id="welcome")
                        yield Static(
                            "Используйте боковую панель или горячие клавиши Alt+W / Alt+F, чтобы открывать модули.",
                            id="menu-description",
                        )
                    with TabPane("Редактор", id="tab-quick"):
                        yield QuickEditorView()
                    with TabPane("Стили", id="tab-styles"):
                        yield StyleManagerView()
                    with TabPane("Персонажи", id="tab-characters"):
                        yield CharacterManagerView()
                    with TabPane("Квесты", id="tab-quests"):
                        yield QuestGeneratorView()
                    with TabPane("Ролевая", id="tab-roleplay"):
                        yield RoleplayView()
                    with TabPane("История", id="tab-history"):
                        yield HistoryView()
        yield Footer()

    async def call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        return await asyncio.to_thread(self.ollama.chat, system_prompt, user_prompt, None)

    async def call_ollama_with_messages(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        return await asyncio.to_thread(self.ollama.chat, system_prompt, None, messages)

    def refresh_history_panels(self) -> None:
        for history_view in self.query(HistoryView):
            history_view.refresh_history()

    def action_open_quick_editor(self) -> None:
        self.open_quick_editor()

    def action_open_main_menu(self) -> None:
        self.open_main_menu()

    def open_quick_editor(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = "tab-quick"

    def open_main_menu(self) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = "tab-menu"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "btn-menu": "tab-menu",
            "btn-quick": "tab-quick",
            "btn-styles": "tab-styles",
            "btn-characters": "tab-characters",
            "btn-quests": "tab-quests",
            "btn-roleplay": "tab-roleplay",
            "btn-history": "tab-history",
        }
        target = mapping.get(event.button.id or "")
        if target:
            tabs = self.query_one("#tabs", TabbedContent)
            tabs.active = target


def run_app() -> None:
    AIHelperApp().run()
