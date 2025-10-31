from __future__ import annotations

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QCheckBox,
    QPushButton,
    QMessageBox,
)

from modules import settings_manager
from modules.ollama_client import OllamaClient


class SettingsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)

        form_layout = QFormLayout()

        self.api_url_input = QLineEdit(self)
        self.api_url_input.setPlaceholderText("http://localhost:11434")
        form_layout.addRow("Ollama API URL", self.api_url_input)

        self.model_combo = QComboBox(self)
        self.model_combo.setEditable(True)
        form_layout.addRow("Модель", self.model_combo)

        self.refresh_models_btn = QPushButton("Обновить список моделей", self)
        self.refresh_models_btn.clicked.connect(self.load_available_models)
        form_layout.addRow("", self.refresh_models_btn)

        self.global_style_input = QTextEdit(self)
        self.global_style_input.setMaximumHeight(100)
        self.global_style_input.setPlaceholderText(
            "Например: Псевдосредневековый стиль с высокопарной речью"
        )
        form_layout.addRow("Общий стиль генерации", self.global_style_input)

        self.save_context_checkbox = QCheckBox("Сохранять контекст диалогов", self)
        form_layout.addRow("", self.save_context_checkbox)

        layout.addLayout(form_layout)

        self.save_btn = QPushButton("Сохранить настройки", self)
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        layout.addStretch(1)

        self.load_settings()

    def load_settings(self) -> None:
        settings = settings_manager.get_settings()
        self.api_url_input.setText(settings.get("ollama_url", "http://localhost:11434"))
        self.model_combo.clear()
        self.model_combo.addItem(settings.get("model", "llama2"))
        self.global_style_input.setPlainText(settings.get("global_style", ""))
        self.save_context_checkbox.setChecked(bool(settings.get("save_dialogue_context", True)))
        self.load_available_models()

    def load_available_models(self) -> None:
        api_url = self.api_url_input.text() or "http://localhost:11434"
        try:
            client = OllamaClient(api_url=api_url)
            models = client.get_available_models()
            current_model = self.model_combo.currentText()
            self.model_combo.clear()
            if models:
                self.model_combo.addItems(models)
                if current_model in models:
                    self.model_combo.setCurrentText(current_model)
                else:
                    self.model_combo.setCurrentText(models[0])
            else:
                if current_model:
                    self.model_combo.addItem(current_model)
                else:
                    self.model_combo.addItem("llama2")
        except RuntimeError as exc:
            QMessageBox.critical(
                self,
                "Ошибка подключения",
                f"{exc}\n\nПроверьте:\n"
                "1. Установлена ли Ollama (https://ollama.ai)\n"
                "2. Запущена ли Ollama (ollama serve)\n"
                "3. Правильность URL в поле выше",
            )
        except Exception as exc:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось загрузить список моделей: {exc}",
            )

    def save_settings(self) -> None:
        api_url = self.api_url_input.text().strip() or "http://localhost:11434"
        model = self.model_combo.currentText().strip() or "llama2"
        global_style = self.global_style_input.toPlainText().strip()
        save_context = self.save_context_checkbox.isChecked()

        try:
            settings_manager.update_settings(
                {
                    "ollama_url": api_url,
                    "model": model,
                    "global_style": global_style,
                    "save_dialogue_context": save_context,
                }
            )
            QMessageBox.information(self, "Успех", "Настройки сохранены")
        except Exception as exc:
            QMessageBox.critical(self, "Ошибка", str(exc))
