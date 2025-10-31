from __future__ import annotations

from typing import List, Callable, Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QLabel,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QDialogButtonBox,
    QMessageBox,
    QComboBox,
    QSplitter,
    QInputDialog,
)

from app.core.models import Scene, SceneMessage
from app.services.world_service import WorldService
from app.core.ollama import OllamaClient
from app.services.prompt_builder import PromptBuilder


class SceneDialog(QDialog):
    def __init__(self, parent=None, scene: Scene | None = None, characters: List[str] | None = None):
        super().__init__(parent)
        self.scene = scene
        self.characters = characters or []
        self.setWindowTitle("Сцена")

        self.title_edit = QLineEdit()
        self.topic_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.participants_edit = QLineEdit()
        self.summary_edit = QTextEdit()
        self.summary_edit.setMinimumHeight(80)

        layout = QFormLayout()
        layout.addRow("Название", self.title_edit)
        layout.addRow("Тема", self.topic_edit)
        layout.addRow("Локация", self.location_edit)
        layout.addRow("Участники (через запятую)", self.participants_edit)
        layout.addRow("Сводка", self.summary_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        if scene:
            self.title_edit.setText(scene.title)
            self.topic_edit.setText(scene.topic)
            self.location_edit.setText(scene.location)
            self.participants_edit.setText(", ".join(scene.participants))
            self.summary_edit.setPlainText(scene.summary)
        elif self.characters:
            self.participants_edit.setText(", ".join(self.characters[:3]))

    def get_data(self) -> Scene:
        participants = [p.strip() for p in self.participants_edit.text().split(",") if p.strip()]
        return Scene(
            id=self.scene.id if self.scene else None,
            title=self.title_edit.text().strip(),
            topic=self.topic_edit.text().strip(),
            location=self.location_edit.text().strip(),
            participants=participants,
            summary=self.summary_edit.toPlainText().strip(),
        )


class VariantWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, ollama: OllamaClient, prompt: str, count: int):
        super().__init__()
        self.ollama = ollama
        self.prompt = prompt
        self.count = count

    def run(self):
        try:
            response = self.ollama.generate(self.prompt)
            variants = self._parse_variants(response)
            if not variants:
                variants = [response.strip()]
            self.finished.emit(variants[: self.count])
        except Exception as exc:
            self.error.emit(str(exc))

    def _parse_variants(self, text: str) -> List[str]:
        variants: List[str] = []
        current = []
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.lower().startswith("вариант") or stripped.lower().startswith("option"):
                if current:
                    variants.append(" ".join(current).strip())
                    current = []
                parts = stripped.split(":", 1)
                if len(parts) == 2:
                    current.append(parts[1].strip())
                else:
                    current.append(stripped)
            else:
                current.append(stripped)
        if current:
            variants.append(" ".join(current).strip())
        return variants


class ContinuationWorker(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ollama: OllamaClient, prompt: str):
        super().__init__()
        self.ollama = ollama
        self.prompt = prompt

    def run(self):
        try:
            response = self.ollama.generate(self.prompt)
            self.finished.emit(response.strip())
        except Exception as exc:
            self.error.emit(str(exc))


class ScenesTab(QWidget):
    def __init__(
        self,
        service: WorldService,
        ollama: OllamaClient,
        prompt_builder: PromptBuilder,
        on_change: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.service = service
        self.ollama = ollama
        self.prompt_builder = prompt_builder
        self.on_change = on_change

        self.current_scene: Scene | None = None
        self.current_variants: List[str] = []

        splitter = QSplitter(Qt.Horizontal)

        # Left panel with scenes list
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        self.scene_list = QListWidget()
        self.scene_list.setAlternatingRowColors(True)
        self.create_scene_btn = QPushButton("Создать сцену")
        self.delete_scene_btn = QPushButton("Удалить сцену")

        left_layout.addWidget(QLabel("Сцены"))
        left_layout.addWidget(self.scene_list)
        left_layout.addWidget(self.create_scene_btn)
        left_layout.addWidget(self.delete_scene_btn)
        left_panel.setLayout(left_layout)

        # Right panel with scene details
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        self.scene_title = QLabel("Выберите сцену")
        self.scene_title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.message_list = QListWidget()
        self.message_list.setAlternatingRowColors(True)
        self.message_list.setContextMenuPolicy(Qt.CustomContextMenu)

        message_actions_layout = QHBoxLayout()
        self.edit_message_btn = QPushButton("✏️ Редактировать реплику")
        self.delete_message_btn = QPushButton("🗑 Удалить реплику")
        message_actions_layout.addWidget(self.edit_message_btn)
        message_actions_layout.addWidget(self.delete_message_btn)

        generator_controls_layout = QHBoxLayout()
        self.speaker_combo = QComboBox()
        self.generate_btn = QPushButton("✨ Сгенерировать варианты")
        self.add_manual_btn = QPushButton("Добавить вручную")
        generator_controls_layout.addWidget(QLabel("Говорящий"))
        generator_controls_layout.addWidget(self.speaker_combo, stretch=1)
        generator_controls_layout.addWidget(self.generate_btn)
        generator_controls_layout.addWidget(self.add_manual_btn)

        self.variants_list = QListWidget()
        self.variants_list.setAlternatingRowColors(True)
        self.variants_list.setSelectionMode(QListWidget.SingleSelection)
        self.variants_list.setMinimumHeight(120)

        self.generated_text = QTextEdit()
        self.generated_text.setPlaceholderText("Выберите вариант или отредактируйте текст перед добавлением")
        self.generated_text.setMinimumHeight(120)

        variant_actions_layout = QHBoxLayout()
        self.accept_btn = QPushButton("✔ Добавить в сцену")
        self.regenerate_btn = QPushButton("🔄 Получить ещё варианты")
        self.continue_btn = QPushButton("➡ Продолжить реплику")
        variant_actions_layout.addWidget(self.accept_btn)
        variant_actions_layout.addWidget(self.continue_btn)
        variant_actions_layout.addWidget(self.regenerate_btn)

        right_layout.addWidget(self.scene_title)
        right_layout.addWidget(QLabel("История сцены"))
        right_layout.addWidget(self.message_list, stretch=2)
        right_layout.addLayout(message_actions_layout)
        right_layout.addSpacing(8)
        right_layout.addLayout(generator_controls_layout)
        right_layout.addWidget(QLabel("Варианты ответа"))
        right_layout.addWidget(self.variants_list, stretch=1)
        right_layout.addWidget(QLabel("Редактирование выбранного варианта"))
        right_layout.addWidget(self.generated_text, stretch=1)
        right_layout.addLayout(variant_actions_layout)
        right_panel.setLayout(right_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self._wire_signals()
        self.refresh()
        self._update_buttons_state(False)

    def _notify_change(self):
        if callable(self.on_change):
            self.on_change()

    # region helpers
    def _wire_signals(self):
        self.scene_list.itemSelectionChanged.connect(self.load_scene)
        self.create_scene_btn.clicked.connect(self.create_scene)
        self.delete_scene_btn.clicked.connect(self.delete_scene)

        self.generate_btn.clicked.connect(self.generate_variants)
        self.regenerate_btn.clicked.connect(self.generate_variants)
        self.continue_btn.clicked.connect(self.continue_variant)
        self.accept_btn.clicked.connect(self.accept_variant)
        self.add_manual_btn.clicked.connect(self.add_manual_line)

        self.edit_message_btn.clicked.connect(self.edit_selected_message)
        self.delete_message_btn.clicked.connect(self.delete_selected_message)
        self.message_list.itemDoubleClicked.connect(self.edit_selected_message)

        self.variants_list.itemSelectionChanged.connect(self._on_variant_selected)

    def _update_buttons_state(self, enable_variants: bool):
        self.accept_btn.setEnabled(enable_variants)
        self.continue_btn.setEnabled(enable_variants)
        self.regenerate_btn.setEnabled(enable_variants)

    def refresh(self):
        self.scene_list.clear()
        scenes = self.service.list_scenes()
        for scene in scenes:
            item = QListWidgetItem(scene.title)
            item.setData(Qt.UserRole, scene)
            self.scene_list.addItem(item)
        if scenes:
            self.scene_list.setCurrentRow(0)

    def _current_scene_from_item(self) -> Scene | None:
        item = self.scene_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    # endregion

    # region scene management
    def create_scene(self):
        characters = [c.name for c in self.service.list_characters()]
        dialog = SceneDialog(self, characters=characters)
        if dialog.exec_() == QDialog.Accepted:
            scene = dialog.get_data()
            if not scene.title:
                QMessageBox.warning(self, "Сцены", "Название не может быть пустым")
                return
            self.service.save_scene(scene)
            self.refresh()
            self._notify_change()

    def delete_scene(self):
        scene = self._current_scene_from_item()
        if not scene:
            return
        confirm = QMessageBox.question(self, "Удаление сцены", f"Удалить сцену '{scene.title}'?")
        if confirm == QMessageBox.Yes:
            self.service.delete_scene(scene.id)
            self.refresh()
            self._notify_change()
            self.current_scene = None
            self.scene_title.setText("Выберите сцену")
            self.message_list.clear()
            self.variants_list.clear()
            self.generated_text.clear()
            self._update_buttons_state(False)

    def load_scene(self):
        scene = self._current_scene_from_item()
        if not scene:
            return
        self.current_scene = scene
        self.scene_title.setText(f"{scene.title} — {scene.location or 'неизвестная локация'}")
        self.speaker_combo.clear()
        self.speaker_combo.addItems(scene.participants)
        self.show_messages()
        self.variants_list.clear()
        self.generated_text.clear()
        self._update_buttons_state(False)

    def show_messages(self):
        if not self.current_scene:
            return
        messages = self.service.list_scene_messages(self.current_scene.id)
        self.message_list.clear()
        working_memory_payload = []
        for message in messages:
            item = QListWidgetItem(f"{message.order_index + 1}. {message.speaker}: {message.content}")
            item.setData(Qt.UserRole, message)
            self.message_list.addItem(item)
            working_memory_payload.append({"speaker": message.speaker, "content": message.content})
        self.service.memory.set_working_memory(self.current_scene.id, working_memory_payload)

    # endregion

    # region generation workflow
    def generate_variants(self):
        if not self.current_scene:
            QMessageBox.warning(self, "Генерация", "Выберите сцену")
            return
        speaker = self.speaker_combo.currentText()
        if not speaker:
            QMessageBox.warning(self, "Генерация", "Добавьте участника сцены")
            return

        base_context = self.prompt_builder.build_scene_context(self.current_scene.id)
        prompt = (
            f"{base_context}\n\n"
            f"Сгенерируй 3 варианта следующей реплики от персонажа {speaker}."
            """ Учитывай характер и предшествующие реплики. 
Ответ представь в формате:
ВАРИАНТ 1: ...
ВАРИАНТ 2: ...
ВАРИАНТ 3: ..."""
        )

        self.generate_btn.setEnabled(False)
        self.regenerate_btn.setEnabled(False)
        self.current_variants = []
        self.variants_list.clear()
        self.generated_text.clear()
        self._update_buttons_state(False)

        self.variant_worker = VariantWorker(self.ollama, prompt, count=3)
        self.variant_worker.finished.connect(self._on_variants_ready)
        self.variant_worker.error.connect(self._on_generation_error)
        self.variant_worker.start()

    def _on_variants_ready(self, variants: List[str]):
        self.generate_btn.setEnabled(True)
        self.regenerate_btn.setEnabled(True)
        self.current_variants = variants
        self.variants_list.clear()
        for index, variant in enumerate(variants, start=1):
            item = QListWidgetItem(f"Вариант {index}: {variant}")
            item.setData(Qt.UserRole, variant)
            self.variants_list.addItem(item)
        if variants:
            self.variants_list.setCurrentRow(0)
            self._update_buttons_state(True)

    def _on_generation_error(self, error: str):
        self.generate_btn.setEnabled(True)
        self.regenerate_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка генерации", f"Не удалось получить ответ от модели:\n{error}")

    def _on_variant_selected(self):
        item = self.variants_list.currentItem()
        if not item:
            self.generated_text.clear()
            self._update_buttons_state(False)
            return
        variant = item.data(Qt.UserRole)
        self.generated_text.setPlainText(variant)
        self._update_buttons_state(True)

    def continue_variant(self):
        text = self.generated_text.toPlainText().strip()
        if not text or not self.current_scene:
            return
        speaker = self.speaker_combo.currentText()
        prompt = (
            f"Продолжи следующую реплику персонажа {speaker} в той же манере."
            f"\nТекст: {text}\nПродолжение:"
        )

        self.continue_btn.setEnabled(False)
        self.continuation_worker = ContinuationWorker(self.ollama, prompt)
        self.continuation_worker.finished.connect(self._on_continuation_ready)
        self.continuation_worker.error.connect(lambda err: self._on_continuation_error(err))
        self.continuation_worker.start()

    def _on_continuation_ready(self, continuation: str):
        self.continue_btn.setEnabled(True)
        if continuation:
            self.generated_text.moveCursor(self.generated_text.textCursor().End)
            if not self.generated_text.toPlainText().endswith(" "):
                self.generated_text.insertPlainText(" ")
            self.generated_text.insertPlainText(continuation)

    def _on_continuation_error(self, error: str):
        self.continue_btn.setEnabled(True)
        QMessageBox.warning(self, "Продолжение", f"Не удалось продолжить реплику:\n{error}")

    def accept_variant(self):
        if not self.current_scene:
            return
        text = self.generated_text.toPlainText().strip()
        if not text:
            QMessageBox.warning(self, "Добавление реплики", "Текст пустой")
            return
        speaker = self.speaker_combo.currentText()
        messages = self.service.list_scene_messages(self.current_scene.id)
        order_index = len(messages)
        self.service.add_scene_message(self.current_scene.id, speaker, text, order_index)
        self.generated_text.clear()
        self.variants_list.clear()
        self.current_variants = []
        self._update_buttons_state(False)
        self.show_messages()

    def add_manual_line(self):
        if not self.current_scene:
            return
        speaker = self.speaker_combo.currentText()
        if not speaker:
            QMessageBox.warning(self, "Реплика", "Выберите говорящего")
            return
        text, ok = QInputDialog.getMultiLineText(self, "Добавить реплику", f"Текст для {speaker}")
        if ok and text.strip():
            messages = self.service.list_scene_messages(self.current_scene.id)
            order_index = len(messages)
            self.service.add_scene_message(self.current_scene.id, speaker, text.strip(), order_index)
            self.show_messages()

    # endregion

    # region message editing
    def selected_message(self) -> SceneMessage | None:
        item = self.message_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def edit_selected_message(self):
        message = self.selected_message()
        if not message:
            return
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Редактирование реплики",
            f"{message.speaker}:",
            message.content,
        )
        if ok and text.strip():
            self.service.update_scene_message(message.id, text.strip())
            self.show_messages()

    def delete_selected_message(self):
        message = self.selected_message()
        if not message:
            return
        confirm = QMessageBox.question(
            self,
            "Удаление реплики",
            f"Удалить реплику {message.speaker}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_scene_message(message.id)
            self.show_messages()

    # endregion
