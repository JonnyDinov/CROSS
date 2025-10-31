from typing import Callable, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDialogButtonBox,
    QApplication,
)

from app.core.models import Character
from app.core.ollama import OllamaClient
from app.services.world_service import WorldService
from app.ui.components.generative_fields import GenerativeLineEdit, GenerativeTextEdit


class CharacterDialog(QDialog):
    def __init__(
        self,
        parent=None,
        character: Optional[Character] = None,
        service: Optional[WorldService] = None,
        ollama: Optional[OllamaClient] = None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Персонаж")
        self.character = character
        self.service = service
        self.ollama = ollama

        self.name_edit = GenerativeLineEdit()
        self.faction_edit = GenerativeLineEdit()
        self.description_edit = GenerativeTextEdit(height=100)
        self.personality_edit = GenerativeTextEdit(height=100)
        self.speech_edit = GenerativeTextEdit(height=100)
        self.goals_edit = GenerativeTextEdit(height=80)
        self.relationships_edit = GenerativeTextEdit(height=80)

        layout = QFormLayout()
        layout.addRow("Имя", self.name_edit)
        layout.addRow("Фракция", self.faction_edit)
        layout.addRow("Описание", self.description_edit)
        layout.addRow("Характер", self.personality_edit)
        layout.addRow("Манера речи", self.speech_edit)
        layout.addRow("Цели", self.goals_edit)
        layout.addRow("Связи", self.relationships_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        self.name_edit.request_generate.connect(lambda: self.generate_field("name"))
        self.faction_edit.request_generate.connect(lambda: self.generate_field("faction"))
        self.description_edit.request_generate.connect(lambda: self.generate_field("description"))
        self.personality_edit.request_generate.connect(lambda: self.generate_field("personality"))
        self.speech_edit.request_generate.connect(lambda: self.generate_field("speech_style"))
        self.goals_edit.request_generate.connect(lambda: self.generate_field("goals"))
        self.relationships_edit.request_generate.connect(lambda: self.generate_field("relationships"))

        if character:
            self.name_edit.setText(character.name)
            self.faction_edit.setText(character.faction)
            self.description_edit.setPlainText(character.description)
            self.personality_edit.setPlainText(character.personality)
            self.speech_edit.setPlainText(character.speech_style)
            self.goals_edit.setPlainText(character.goals)
            self.relationships_edit.setPlainText(character.relationships)

    def _context_prompt(self) -> str:
        parts = []
        if self.character:
            parts.append(f"Имя: {self.character.name}")
        name = self.name_edit.text()
        if name:
            parts.append(f"Текущее имя: {name}")
        faction = self.faction_edit.text()
        if faction:
            parts.append(f"Фракция: {faction}")
        description = self.description_edit.toPlainText().strip()
        if description:
            parts.append(f"Описание: {description}")
        personality = self.personality_edit.toPlainText().strip()
        if personality:
            parts.append(f"Характер: {personality}")
        speech = self.speech_edit.toPlainText().strip()
        if speech:
            parts.append(f"Манера речи: {speech}")
        goals = self.goals_edit.toPlainText().strip()
        if goals:
            parts.append(f"Цели: {goals}")
        relations = self.relationships_edit.toPlainText().strip()
        if relations:
            parts.append(f"Связи: {relations}")
        return "\n".join(parts)

    def generate_field(self, field: str):
        if not self.ollama:
            return
        instructions = {
            "name": "Придумай яркое имя для персонажа в фэнтези-сеттинге.",
            "faction": "Предложи фракцию или организацию, к которой может принадлежать персонаж.",
            "description": "Опиши внешность и роль персонажа несколькими насыщенными предложениями.",
            "personality": "Опиши характер персонажа, его темперамент и мировоззрение.",
            "speech_style": "Опиши манеру речи персонажа — темп, словарный запас, типичные выражения.",
            "goals": "Опиши ключевые цели и мотивацию персонажа.",
            "relationships": "Опиши отношения персонажа с другими, связи и конфликты.",
        }
        prompt_instruction = instructions.get(field)
        if not prompt_instruction:
            return
        context = self._context_prompt()
        prompt = (
            "Ты творческий ассистент, помогающий автору ролевого мира."
            "\nИспользуй следующий контекст:"
        )
        if context:
            prompt += f"\n{context}"
        prompt += f"\n\n{prompt_instruction}\nОтвет предоставь кратко и по делу."

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            result = self.ollama.generate(prompt)
        finally:
            QApplication.restoreOverrideCursor()
        if not result:
            return

        setter_map = {
            "name": self.name_edit.setText,
            "faction": self.faction_edit.setText,
            "description": self.description_edit.setPlainText,
            "personality": self.personality_edit.setPlainText,
            "speech_style": self.speech_edit.setPlainText,
            "goals": self.goals_edit.setPlainText,
            "relationships": self.relationships_edit.setPlainText,
        }
        setter = setter_map.get(field)
        if setter:
            setter(result.strip())

    def get_data(self) -> Character:
        character_id = self.character.id if self.character else None
        return Character(
            id=character_id,
            name=self.name_edit.text().strip(),
            description=self.description_edit.toPlainText().strip(),
            personality=self.personality_edit.toPlainText().strip(),
            speech_style=self.speech_edit.toPlainText().strip(),
            goals=self.goals_edit.toPlainText().strip(),
            relationships=self.relationships_edit.toPlainText().strip(),
            faction=self.faction_edit.text().strip(),
        )


class CharactersTab(QWidget):
    def __init__(
        self,
        service: WorldService,
        ollama: OllamaClient,
        on_change: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.service = service
        self.ollama = ollama
        self.on_change = on_change

        self.list_widget = QListWidget()
        self.detail_label = QLabel("Выберите персонажа")
        self.detail_label.setWordWrap(True)

        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(self.detail_label)
        self.setLayout(layout)

        self.list_widget.itemSelectionChanged.connect(self.show_details)
        self.add_button.clicked.connect(self.create_character)
        self.edit_button.clicked.connect(self.edit_character)
        self.delete_button.clicked.connect(self.delete_character)

        self.refresh()

    def _notify_change(self):
        if callable(self.on_change):
            self.on_change()

    def refresh(self):
        self.list_widget.clear()
        characters = self.service.list_characters()
        for character in characters:
            item = QListWidgetItem(character.name)
            item.setData(Qt.UserRole, character)
            self.list_widget.addItem(item)

    def selected_character(self) -> Optional[Character]:
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def show_details(self):
        character = self.selected_character()
        if not character:
            self.detail_label.setText("Выберите персонажа")
            return

        details = [
            f"<b>{character.name}</b>",
            f"Фракция: {character.faction}",
            f"Описание: {character.description}",
            f"Характер: {character.personality}",
            f"Манера речи: {character.speech_style}",
            f"Цели: {character.goals}",
            f"Связи: {character.relationships}",
        ]
        self.detail_label.setText("<br>".join(details))

    def create_character(self):
        dialog = CharacterDialog(self, service=self.service, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            character = dialog.get_data()
            self.service.save_character(character)
            self.refresh()
            self._notify_change()

    def edit_character(self):
        character = self.selected_character()
        if not character:
            QMessageBox.warning(self, "Персонажи", "Выберите персонажа для редактирования")
            return

        dialog = CharacterDialog(self, character, service=self.service, ollama=self.ollama)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            updated.id = character.id
            self.service.save_character(updated)
            self.refresh()
            self._notify_change()

    def delete_character(self):
        character = self.selected_character()
        if not character:
            return

        confirm = QMessageBox.question(
            self,
            "Удаление персонажа",
            f"Удалить {character.name}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_character(character.id)
            self.refresh()
            self._notify_change()
