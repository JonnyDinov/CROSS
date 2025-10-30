from __future__ import annotations

from typing import List

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QApplication,
)

from modules import character_manager, dialogue_manager, lore_manager, settings_manager
from modules.ollama_client import OllamaClient


class DialogueWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, client: OllamaClient, messages: List[dict]):
        super().__init__()
        self.client = client
        self.messages = messages

    def run(self) -> None:
        try:
            response = self.client.chat(self.messages)
            if response:
                self.finished.emit(response)
            else:
                self.error.emit("Не удалось получить ответ от Ollama")
        except Exception as exc:
            self.error.emit(str(exc))


class DialoguesTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._worker: DialogueWorker | None = None

        layout = QVBoxLayout(self)

        char_layout = QHBoxLayout()
        char_layout.addWidget(QLabel("Персонаж:"))
        self.character_combo = QComboBox(self)
        self.character_combo.currentIndexChanged.connect(self.on_character_changed)
        char_layout.addWidget(self.character_combo, 1)
        layout.addLayout(char_layout)

        layout.addWidget(QLabel("История последних диалогов:"))
        self.history_text = QTextEdit(self)
        self.history_text.setReadOnly(True)
        self.history_text.setMaximumHeight(150)
        layout.addWidget(self.history_text)

        layout.addWidget(QLabel("Реплика игрока:"))
        self.player_input = QTextEdit(self)
        self.player_input.setMaximumHeight(100)
        self.player_input.setPlaceholderText("Введите вашу реплику...")
        layout.addWidget(self.player_input)

        self.generate_btn = QPushButton("Сгенерировать ответ ИИ", self)
        self.generate_btn.clicked.connect(self.generate_response)
        layout.addWidget(self.generate_btn)

        layout.addWidget(QLabel("Ответ персонажа:"))
        self.response_text = QTextEdit(self)
        self.response_text.setPlaceholderText("Ответ появится здесь...")
        layout.addWidget(self.response_text)

        button_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Скопировать текст", self)
        self.copy_btn.clicked.connect(self.copy_response)
        button_layout.addWidget(self.copy_btn)

        self.save_btn = QPushButton("Сохранить диалог", self)
        self.save_btn.clicked.connect(self.save_dialogue)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

        self.load_characters()

    def load_characters(self) -> None:
        self.character_combo.clear()
        characters = character_manager.list_characters()
        for char in characters:
            self.character_combo.addItem(char["name"], char["id"])

        if self.character_combo.count() > 0:
            self.on_character_changed()

    def on_character_changed(self) -> None:
        character_id = self.character_combo.currentData()
        if not character_id:
            self.history_text.clear()
            return

        history = dialogue_manager.get_recent_dialogues(character_id, limit=5)
        lines = []
        for entry in history:
            lines.append(f"Игрок: {entry['player_line']}")
            lines.append(f"Персонаж: {entry['ai_response']}")
            lines.append("")
        self.history_text.setPlainText("\n".join(lines))

    def generate_response(self) -> None:
        character_id = self.character_combo.currentData()
        if not character_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите персонажа")
            return

        player_message = self.player_input.toPlainText().strip()
        if not player_message:
            QMessageBox.warning(self, "Предупреждение", "Введите реплику игрока")
            return

        character = character_manager.get_character(character_id)
        if not character:
            QMessageBox.critical(self, "Ошибка", "Персонаж не найден")
            return

        settings = settings_manager.get_settings()
        lore = lore_manager.get_lore()

        system_prompt = f"""
Контекст мира:
{lore}

Ты играешь роль персонажа:
Имя: {character['name']}
Характер: {character['personality'] or 'Не указано'}
Стиль речи: {character['speech_style'] or 'Нейтральный'}
История: {character['backstory'] or 'Не указана'}
Роль в мире: {character['world_role'] or 'Не указана'}

Стиль повествования: {settings.get('global_style', '')}

Отвечай от лица этого персонажа, используя его стиль речи и характер.
""".strip()

        messages = [{"role": "system", "content": system_prompt}]

        if settings.get("save_dialogue_context", False):
            history = dialogue_manager.get_recent_dialogues(character_id, limit=3)
            for entry in history:
                messages.append({"role": "user", "content": entry["player_line"]})
                messages.append({"role": "assistant", "content": entry["ai_response"]})

        messages.append({"role": "user", "content": player_message})

        client = OllamaClient(
            api_url=settings.get("ollama_url", "http://localhost:11434"),
            model=settings.get("model", "llama2"),
        )

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Генерация...")

        self._worker = DialogueWorker(client, messages)
        self._worker.finished.connect(self.on_response_finished)
        self._worker.error.connect(self.on_response_error)
        self._worker.start()

    def on_response_finished(self, response: str) -> None:
        self.response_text.setPlainText(response)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Сгенерировать ответ ИИ")
        self._worker = None

    def on_response_error(self, error: str) -> None:
        QMessageBox.critical(self, "Ошибка", error)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Сгенерировать ответ ИИ")
        self._worker = None

    def copy_response(self) -> None:
        response = self.response_text.toPlainText()
        if response:
            QApplication.clipboard().setText(response)
            QMessageBox.information(self, "Успех", "Текст скопирован в буфер обмена")
        else:
            QMessageBox.warning(self, "Предупреждение", "Нет текста для копирования")

    def save_dialogue(self) -> None:
        character_id = self.character_combo.currentData()
        if not character_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите персонажа")
            return

        player_message = self.player_input.toPlainText().strip()
        ai_response = self.response_text.toPlainText().strip()

        if not player_message or not ai_response:
            QMessageBox.warning(self, "Предупреждение", "Нет данных для сохранения")
            return

        try:
            dialogue_manager.add_dialogue(character_id, player_message, ai_response)
            QMessageBox.information(self, "Успех", "Диалог сохранён")
            self.player_input.clear()
            self.response_text.clear()
            self.on_character_changed()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
