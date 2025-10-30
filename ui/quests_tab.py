from __future__ import annotations

from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QMessageBox,
)

from modules import character_manager, event_manager, lore_manager, settings_manager
from modules.ollama_client import OllamaClient, OllamaWorker


THEMES = [
    "Политика",
    "Война",
    "Тайна",
    "Быт",
    "Мистика",
    "Приключение",
    "Экономика",
    "Интрига",
    "Религия",
]

STYLES = [
    "Героический",
    "Трагический",
    "Сатирический",
    "Эпический",
    "Драматический",
    "Лирический",
]


class EventsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.current_event_id = None
        self._worker: OllamaWorker | None = None

        main_layout = QHBoxLayout(self)

        # Left: list of events
        list_layout = QVBoxLayout()
        list_label = QLabel("События и квесты")
        list_label.setStyleSheet("font-weight: bold;")
        list_layout.addWidget(list_label)

        self.events_list = QListWidget(self)
        self.events_list.currentItemChanged.connect(self.on_event_selected)
        list_layout.addWidget(self.events_list)

        list_buttons_layout = QHBoxLayout()
        self.new_event_btn = QPushButton("Новое событие", self)
        self.new_event_btn.clicked.connect(self.create_new_event)
        list_buttons_layout.addWidget(self.new_event_btn)

        self.delete_event_btn = QPushButton("Удалить", self)
        self.delete_event_btn.clicked.connect(self.delete_event)
        list_buttons_layout.addWidget(self.delete_event_btn)

        list_layout.addLayout(list_buttons_layout)

        main_layout.addLayout(list_layout, 1)

        # Right: form
        form_layout = QVBoxLayout()

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Название события или квеста")
        form_layout.addWidget(QLabel("Название"))
        form_layout.addWidget(self.title_input)

        self.theme_combo = QComboBox(self)
        self.theme_combo.setEditable(True)
        self.theme_combo.addItems(THEMES)
        form_layout.addWidget(QLabel("Тема"))
        form_layout.addWidget(self.theme_combo)

        self.style_combo = QComboBox(self)
        self.style_combo.setEditable(True)
        self.style_combo.addItems(STYLES)
        form_layout.addWidget(QLabel("Стиль повествования"))
        form_layout.addWidget(self.style_combo)

        form_layout.addWidget(QLabel("Участники (персонажи)"))
        self.characters_list = QListWidget(self)
        self.characters_list.setSelectionMode(QListWidget.MultiSelection)
        form_layout.addWidget(self.characters_list)

        self.content_edit = QTextEdit(self)
        self.content_edit.setPlaceholderText("Описание события или квеста...")
        form_layout.addWidget(QLabel("Описание"))
        form_layout.addWidget(self.content_edit, 1)

        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("Сгенерировать при помощи ИИ", self)
        self.generate_btn.clicked.connect(self.generate_with_ai)
        buttons_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("Сохранить", self)
        self.save_btn.clicked.connect(self.save_event)
        buttons_layout.addWidget(self.save_btn)

        form_layout.addLayout(buttons_layout)

        main_layout.addLayout(form_layout, 2)

        self.refresh_characters()
        self.load_events()

    # Loading helpers
    def refresh_characters(self) -> None:
        self.characters_list.clear()
        characters = character_manager.list_characters()
        for char in characters:
            item = QListWidgetItem(char["name"])
            item.setData(Qt.UserRole, char["id"])
            item.setCheckState(Qt.Unchecked)
            self.characters_list.addItem(item)

    def load_events(self) -> None:
        self.events_list.clear()
        events = event_manager.list_events()
        for event in events:
            title = event["title"] or "Без названия"
            theme = event["theme"] or "Без темы"
            text = f"{title} — {theme}"
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, event["id"])
            self.events_list.addItem(item)

    def on_event_selected(self, current: QListWidgetItem) -> None:
        if not current:
            self.current_event_id = None
            self.clear_form()
            return

        event_id = current.data(Qt.UserRole)
        event = event_manager.get_event(event_id)
        if not event:
            self.current_event_id = None
            self.clear_form()
            return

        self.current_event_id = event_id
        self.title_input.setText(event["title"])
        self.theme_combo.setCurrentText(event["theme"])
        self.style_combo.setCurrentText(event["narrative_style"])
        self.content_edit.setPlainText(event["content"])

        # Restore character checks
        selected_ids = set(event["involved_characters"])
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            char_id = item.data(Qt.UserRole)
            item.setCheckState(Qt.Checked if char_id in selected_ids else Qt.Unchecked)

    def clear_form(self) -> None:
        self.title_input.clear()
        self.theme_combo.setCurrentText("")
        self.style_combo.setCurrentText("")
        self.content_edit.clear()
        for i in range(self.characters_list.count()):
            self.characters_list.item(i).setCheckState(Qt.Unchecked)

    # CRUD
    def create_new_event(self) -> None:
        self.current_event_id = None
        self.events_list.clearSelection()
        self.clear_form()
        self.title_input.setFocus()

    def save_event(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Предупреждение", "Укажите название события")
            return

        data = {
            "title": title,
            "theme": self.theme_combo.currentText().strip(),
            "narrative_style": self.style_combo.currentText().strip(),
            "content": self.content_edit.toPlainText().strip(),
            "involved_characters": self._selected_character_ids(),
        }

        try:
            if self.current_event_id:
                event_manager.update_event(self.current_event_id, data)
                QMessageBox.information(self, "Успех", "Событие обновлено")
            else:
                new_id = event_manager.create_event(data)
                self.current_event_id = new_id
                QMessageBox.information(self, "Успех", "Событие создано")
            self.load_events()
            self._reselect_current_event()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    def delete_event(self) -> None:
        if not self.current_event_id:
            QMessageBox.warning(self, "Предупреждение", "Выберите событие для удаления")
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Удалить выбранное событие?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        try:
            event_manager.delete_event(self.current_event_id)
            QMessageBox.information(self, "Успех", "Событие удалено")
            self.current_event_id = None
            self.load_events()
            self.clear_form()
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))

    # AI generation
    def generate_with_ai(self) -> None:
        title = self.title_input.text().strip() or "Неизвестное событие"
        theme = self.theme_combo.currentText().strip()
        narrative_style = self.style_combo.currentText().strip()
        selected_ids = self._selected_character_ids()

        if not theme or not narrative_style:
            QMessageBox.warning(self, "Предупреждение", "Укажите тему и стиль повествования")
            return

        settings = settings_manager.get_settings()
        lore = lore_manager.get_lore()

        characters = [character_manager.get_character(cid) for cid in selected_ids]
        characters = [c for c in characters if c]

        characters_block = ""
        if characters:
            formatted = []
            for char in characters:
                formatted.append(
                    "\n".join(
                        [
                            f"Имя: {char['name']}",
                            f"Характер: {char['personality'] or 'Не указан'}",
                            f"Стиль речи: {char['speech_style'] or 'Не указан'}",
                            f"Роль: {char['world_role'] or 'Не указана'}",
                            f"История: {char['backstory'] or 'Не указана'}",
                        ]
                    )
                )
            characters_block = "\n\nВыбранные персонажи:\n" + "\n---\n".join(formatted)

        prompt = f"""
Создай подробное событие или квест для фэнтезийной ролевой игры.
Название: {title}
Тема: {theme}
Желаемый стиль повествования: {narrative_style}

Контекст мира:
{lore}
{characters_block}

Опиши завязку, ключевых участников, конфликт и несколько возможных исходов.
""".strip()

        system_prompt = (
            "Ты мастер игры в средневековом фэнтезийном мире. "
            "Создавай атмосферные и логичные события, учитывая предоставленный лор и персонажей. "
            f"Общий стиль: {settings.get('global_style', '')}"
        )

        client = OllamaClient(
            api_url=settings.get("ollama_url", "http://localhost:11434"),
            model=settings.get("model", "llama2"),
        )

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Генерация...")

        self._worker = OllamaWorker(client=client, prompt=prompt, system=system_prompt)
        self._worker.finished.connect(self._on_generation_success)
        self._worker.error.connect(self._on_generation_error)
        self._worker.start()

    def _on_generation_success(self, text: str) -> None:
        self.content_edit.setPlainText(text)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Сгенерировать при помощи ИИ")
        self._worker = None

    def _on_generation_error(self, error: str) -> None:
        QMessageBox.critical(self, "Ошибка", error)
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Сгенерировать при помощи ИИ")
        self._worker = None

    # Helpers
    def _selected_character_ids(self) -> List[int]:
        ids: List[int] = []
        for i in range(self.characters_list.count()):
            item = self.characters_list.item(i)
            if item.checkState() == Qt.Checked:
                ids.append(item.data(Qt.UserRole))
        return ids

    def _reselect_current_event(self) -> None:
        if not self.current_event_id:
            return
        for i in range(self.events_list.count()):
            item = self.events_list.item(i)
            if item.data(Qt.UserRole) == self.current_event_id:
                self.events_list.setCurrentRow(i)
                break
