from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QDialog,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QHeaderView,
)

from modules import character_manager


class CharacterDialog(QDialog):
    def __init__(self, parent=None, character_data=None):
        super().__init__(parent)
        self.setWindowTitle("Редактировать персонажа" if character_data else "Добавить персонажа")
        self.setMinimumSize(500, 400)
        self.character_data = character_data

        layout = QFormLayout(self)

        self.name_input = QLineEdit(self)
        layout.addRow("Имя:", self.name_input)

        self.personality_input = QTextEdit(self)
        self.personality_input.setMaximumHeight(80)
        layout.addRow("Характер:", self.personality_input)

        self.speech_input = QTextEdit(self)
        self.speech_input.setMaximumHeight(80)
        layout.addRow("Стиль речи:", self.speech_input)

        self.backstory_input = QTextEdit(self)
        self.backstory_input.setMaximumHeight(100)
        layout.addRow("История:", self.backstory_input)

        self.role_input = QLineEdit(self)
        layout.addRow("Роль в мире:", self.role_input)

        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.accept)
        layout.addWidget(self.save_button)

        if character_data:
            self.load_character_data(character_data)

    def load_character_data(self, data):
        self.name_input.setText(data.get("name", ""))
        self.personality_input.setPlainText(data.get("personality", ""))
        self.speech_input.setPlainText(data.get("speech_style", ""))
        self.backstory_input.setPlainText(data.get("backstory", ""))
        self.role_input.setText(data.get("world_role", ""))

    def get_character_data(self):
        return {
            "name": self.name_input.text(),
            "personality": self.personality_input.toPlainText(),
            "speech_style": self.speech_input.toPlainText(),
            "backstory": self.backstory_input.toPlainText(),
            "world_role": self.role_input.text()
        }


class CharactersTab(QWidget):
    characters_updated = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Имя", "Характер", "Стиль речи", "История", "Роль"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Добавить", self)
        self.add_button.clicked.connect(self.add_character)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Редактировать", self)
        self.edit_button.clicked.connect(self.edit_character)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Удалить", self)
        self.delete_button.clicked.connect(self.delete_character)
        button_layout.addWidget(self.delete_button)

        self.layout.addLayout(button_layout)

        self.load_characters()

    def load_characters(self):
        try:
            characters = character_manager.list_characters()
            self.table.setRowCount(len(characters))

            for i, char in enumerate(characters):
                self.table.setItem(i, 0, QTableWidgetItem(char["name"]))
                self.table.setItem(i, 1, QTableWidgetItem(char["personality"]))
                self.table.setItem(i, 2, QTableWidgetItem(char["speech_style"]))
                self.table.setItem(i, 3, QTableWidgetItem(char["backstory"]))
                self.table.setItem(i, 4, QTableWidgetItem(char["world_role"]))

                for col in range(5):
                    if self.table.item(i, col):
                        self.table.item(i, col).setData(100, char["id"])
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_character(self):
        dialog = CharacterDialog(self)
        if dialog.exec_():
            try:
                data = dialog.get_character_data()
                character_manager.create_character(data)
                self.load_characters()
                self.characters_updated.emit()
                QMessageBox.information(self, "Успех", "Персонаж добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_character(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите персонажа для редактирования")
            return

        character_id = self.table.item(current_row, 0).data(100)
        character = character_manager.get_character(character_id)

        if character:
            dialog = CharacterDialog(self, character)
            if dialog.exec_():
                try:
                    new_data = dialog.get_character_data()
                    character_manager.update_character(character_id, new_data)
                    self.load_characters()
                    self.characters_updated.emit()
                    QMessageBox.information(self, "Успех", "Персонаж обновлён")
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", str(e))

    def delete_character(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Выберите персонажа для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение", "Вы уверены, что хотите удалить персонажа?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                character_id = self.table.item(current_row, 0).data(100)
                character_manager.delete_character(character_id)
                self.load_characters()
                self.characters_updated.emit()
                QMessageBox.information(self, "Успех", "Персонаж удалён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))
