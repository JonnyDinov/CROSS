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
    QProgressDialog,
)

from app.core.models import Quest
from app.services.world_service import WorldService
from app.core.ollama import OllamaClient


class QuestGeneratorWorker(QThread):
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, ollama: OllamaClient, world_context: str, count: int):
        super().__init__()
        self.ollama = ollama
        self.world_context = world_context
        self.count = count

    def run(self):
        try:
            prompt = f"""На основе лора мира сгенерируй {self.count} квеста.

Контекст мира:
{self.world_context}

Для каждого квеста укажи:
1. Название
2. Тип (главный/побочный)
3. Описание
4. Награды
5. Требования

Формат ответа:
КВЕСТ: [название]
ТИП: [главный/побочный]
ОПИСАНИЕ: [описание]
НАГРАДЫ: [награды]
ТРЕБОВАНИЯ: [требования]
---
"""
            result = self.ollama.generate(prompt)
            quests = self._parse_quests(result)
            self.finished.emit(quests)
        except Exception as e:
            self.error.emit(str(e))

    def _parse_quests(self, text: str) -> list:
        quests = []
        quest_blocks = text.split("---")
        
        for block in quest_blocks:
            lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
            if not lines:
                continue
            
            quest_data = {
                "title": "",
                "quest_type": "побочный",
                "description": "",
                "rewards": "",
                "prerequisites": "",
            }
            
            current_key = None
            for line in lines:
                if line.startswith("КВЕСТ:"):
                    quest_data["title"] = line.replace("КВЕСТ:", "").strip()
                elif line.startswith("ТИП:"):
                    quest_data["quest_type"] = line.replace("ТИП:", "").strip()
                elif line.startswith("ОПИСАНИЕ:"):
                    current_key = "description"
                    quest_data["description"] = line.replace("ОПИСАНИЕ:", "").strip()
                elif line.startswith("НАГРАДЫ:"):
                    current_key = "rewards"
                    quest_data["rewards"] = line.replace("НАГРАДЫ:", "").strip()
                elif line.startswith("ТРЕБОВАНИЯ:"):
                    current_key = "prerequisites"
                    quest_data["prerequisites"] = line.replace("ТРЕБОВАНИЯ:", "").strip()
                elif current_key:
                    quest_data[current_key] += " " + line
            
            if quest_data["title"]:
                quests.append(Quest(
                    id=None,
                    title=quest_data["title"],
                    quest_type=quest_data["quest_type"],
                    description=quest_data["description"],
                    rewards=quest_data["rewards"],
                    prerequisites=quest_data["prerequisites"],
                ))
        
        return quests


class QuestDialog(QDialog):
    def __init__(self, parent=None, quest: Quest = None):
        super().__init__(parent)
        self.quest = quest
        self.setWindowTitle("Квест")

        self.title_edit = QLineEdit()
        self.type_edit = QComboBox()
        self.type_edit.setEditable(True)
        self.type_edit.addItems(["главный", "побочный", "микро-событие"])
        self.description_edit = QTextEdit()
        self.rewards_edit = QTextEdit()
        self.prerequisites_edit = QTextEdit()

        layout = QFormLayout()
        layout.addRow("Название", self.title_edit)
        layout.addRow("Тип", self.type_edit)
        layout.addRow("Описание", self.description_edit)
        layout.addRow("Награды", self.rewards_edit)
        layout.addRow("Требования", self.prerequisites_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

        if quest:
            self.title_edit.setText(quest.title)
            index = self.type_edit.findText(quest.quest_type)
            if index >= 0:
                self.type_edit.setCurrentIndex(index)
            else:
                self.type_edit.setEditText(quest.quest_type)
            self.description_edit.setPlainText(quest.description)
            self.rewards_edit.setPlainText(quest.rewards)
            self.prerequisites_edit.setPlainText(quest.prerequisites)

    def get_data(self) -> Quest:
        return Quest(
            id=self.quest.id if self.quest else None,
            title=self.title_edit.text(),
            quest_type=self.type_edit.currentText(),
            description=self.description_edit.toPlainText(),
            rewards=self.rewards_edit.toPlainText(),
            prerequisites=self.prerequisites_edit.toPlainText(),
        )


class QuestsTab(QWidget):
    def __init__(self, service: WorldService, ollama: OllamaClient, parent=None):
        super().__init__(parent)
        self.service = service
        self.ollama = ollama

        self.list_widget = QListWidget()
        self.detail_label = QLabel("Выберите квест")
        self.detail_label.setWordWrap(True)

        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("Добавить")
        self.generate_button = QPushButton("✨ Сгенерировать квесты")
        self.edit_button = QPushButton("Редактировать")
        self.delete_button = QPushButton("Удалить")

        btn_layout.addWidget(self.add_button)
        btn_layout.addWidget(self.generate_button)
        btn_layout.addWidget(self.edit_button)
        btn_layout.addWidget(self.delete_button)

        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addLayout(btn_layout)
        layout.addWidget(self.detail_label)
        self.setLayout(layout)

        self.list_widget.itemSelectionChanged.connect(self.show_details)
        self.add_button.clicked.connect(self.create_quest)
        self.generate_button.clicked.connect(self.generate_quests)
        self.edit_button.clicked.connect(self.edit_quest)
        self.delete_button.clicked.connect(self.delete_quest)

        self.refresh()

    def refresh(self):
        self.list_widget.clear()
        quests = self.service.list_quests()
        for quest in quests:
            item = QListWidgetItem(f"{quest.quest_type} / {quest.title}")
            item.setData(Qt.UserRole, quest)
            self.list_widget.addItem(item)

    def selected_quest(self) -> Quest:
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None

    def show_details(self):
        quest = self.selected_quest()
        if not quest:
            self.detail_label.setText("Выберите квест")
            return

        details = [
            f"<b>{quest.title}</b>",
            f"Тип: {quest.quest_type}",
            f"Описание: {quest.description}",
            f"Награды: {quest.rewards}",
            f"Требования: {quest.prerequisites}",
        ]
        self.detail_label.setText("<br>".join(details))

    def create_quest(self):
        dialog = QuestDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            quest = dialog.get_data()
            self.service.save_quest(quest)
            self.refresh()

    def edit_quest(self):
        quest = self.selected_quest()
        if not quest:
            QMessageBox.warning(self, "Квесты", "Выберите квест для редактирования")
            return

        dialog = QuestDialog(self, quest)
        if dialog.exec_() == QDialog.Accepted:
            updated = dialog.get_data()
            self.service.save_quest(updated)
            self.refresh()

    def delete_quest(self):
        quest = self.selected_quest()
        if not quest:
            return

        confirm = QMessageBox.question(
            self,
            "Удаление квеста",
            f"Удалить {quest.title}?",
        )
        if confirm == QMessageBox.Yes:
            self.service.delete_quest(quest.id)
            self.refresh()

    def generate_quests(self):
        lore_items = self.service.list_lore()
        if not lore_items:
            QMessageBox.warning(
                self,
                "Генерация квестов",
                "Добавьте сначала лор мира для генерации квестов",
            )
            return

        world_context = "\n".join([
            f"{item.title}: {item.summary}"
            for item in lore_items[:10]
        ])

        progress = QProgressDialog("Генерация квестов...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()

        self.worker = QuestGeneratorWorker(self.ollama, world_context, 3)
        self.worker.finished.connect(lambda quests: self._on_quests_generated(quests, progress))
        self.worker.error.connect(lambda err: self._on_generation_error(err, progress))
        self.worker.start()

    def _on_quests_generated(self, quests: list, progress: QProgressDialog):
        progress.close()
        if not quests:
            QMessageBox.information(self, "Генерация квестов", "Не удалось сгенерировать квесты")
            return

        for quest in quests:
            self.service.save_quest(quest)

        self.refresh()
        QMessageBox.information(
            self,
            "Генерация квестов",
            f"Сгенерировано {len(quests)} квестов",
        )

    def _on_generation_error(self, error: str, progress: QProgressDialog):
        progress.close()
        QMessageBox.critical(
            self,
            "Ошибка генерации",
            f"Не удалось сгенерировать квесты:\n{error}",
        )
