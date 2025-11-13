from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QScrollArea,
    QHBoxLayout,
)

from agent.config import config
from agent.integrations.ollama_client import ollama_client


class SettingsPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header = QLabel("Settings")
        header.setObjectName("HeaderLabel")
        layout.addWidget(header)

        ollama_group = self._build_ollama_group()
        layout.addWidget(ollama_group)

        hotkeys_group = self._build_hotkeys_group()
        layout.addWidget(hotkeys_group)

        agent_group = self._build_agent_group()
        layout.addWidget(agent_group)

        security_group = self._build_security_group()
        layout.addWidget(security_group)

        gui_group = self._build_gui_group()
        layout.addWidget(gui_group)

        button_row = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self._save_settings)
        button_row.addWidget(self.save_button)

        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.setObjectName("SecondaryButton")
        self.reset_button.clicked.connect(self._reset_settings)
        button_row.addWidget(self.reset_button)

        layout.addLayout(button_row)
        layout.addStretch()

        scroll.setWidget(scroll_content)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _build_ollama_group(self) -> QGroupBox:
        group = QGroupBox("Ollama Configuration")
        form = QFormLayout()

        self.ollama_url = QLineEdit()
        form.addRow("Base URL:", self.ollama_url)

        self.ollama_model = QComboBox()
        self._load_models()
        form.addRow("Model:", self.ollama_model)

        self.ollama_vision_model = QComboBox()
        form.addRow("Vision Model:", self.ollama_vision_model)

        self.ollama_timeout = QSpinBox()
        self.ollama_timeout.setRange(10, 600)
        self.ollama_timeout.setSuffix(" seconds")
        form.addRow("Timeout:", self.ollama_timeout)

        self.ollama_temperature = QDoubleSpinBox()
        self.ollama_temperature.setRange(0.0, 2.0)
        self.ollama_temperature.setSingleStep(0.1)
        form.addRow("Temperature:", self.ollama_temperature)

        self.refresh_models_button = QPushButton("Refresh Models")
        self.refresh_models_button.setObjectName("SecondaryButton")
        self.refresh_models_button.clicked.connect(self._load_models)
        form.addRow("", self.refresh_models_button)

        group.setLayout(form)
        return group

    def _build_hotkeys_group(self) -> QGroupBox:
        group = QGroupBox("Hotkeys")
        form = QFormLayout()

        self.hotkey_prompt = QLineEdit()
        form.addRow("Prompt Panel:", self.hotkey_prompt)

        self.hotkey_text = QLineEdit()
        form.addRow("Text Processing:", self.hotkey_text)

        group.setLayout(form)
        return group

    def _build_agent_group(self) -> QGroupBox:
        group = QGroupBox("Agent Settings")
        form = QFormLayout()

        self.agent_update_freq = QDoubleSpinBox()
        self.agent_update_freq.setRange(0.1, 10.0)
        self.agent_update_freq.setSingleStep(0.1)
        self.agent_update_freq.setSuffix(" seconds")
        form.addRow("Update Frequency:", self.agent_update_freq)

        self.agent_max_history = QSpinBox()
        self.agent_max_history.setRange(10, 1000)
        form.addRow("Max History:", self.agent_max_history)

        self.agent_log_level = QComboBox()
        self.agent_log_level.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        form.addRow("Log Level:", self.agent_log_level)

        self.agent_autostart = QCheckBox("Start with Windows")
        form.addRow("", self.agent_autostart)

        group.setLayout(form)
        return group

    def _build_security_group(self) -> QGroupBox:
        group = QGroupBox("Security Settings")
        form = QFormLayout()

        self.security_confirm_delete = QCheckBox("Require confirmation for delete operations")
        form.addRow("", self.security_confirm_delete)

        self.security_confirm_execute = QCheckBox("Require confirmation for execute operations")
        form.addRow("", self.security_confirm_execute)

        group.setLayout(form)
        return group

    def _build_gui_group(self) -> QGroupBox:
        group = QGroupBox("GUI Settings")
        form = QFormLayout()

        self.gui_opacity = QDoubleSpinBox()
        self.gui_opacity.setRange(0.5, 1.0)
        self.gui_opacity.setSingleStep(0.05)
        form.addRow("Opacity:", self.gui_opacity)

        self.gui_font_size = QSpinBox()
        self.gui_font_size.setRange(8, 24)
        form.addRow("Font Size:", self.gui_font_size)

        self.gui_animation = QSpinBox()
        self.gui_animation.setRange(0, 1000)
        self.gui_animation.setSuffix(" ms")
        form.addRow("Animation Duration:", self.gui_animation)

        group.setLayout(form)
        return group

    def _load_models(self):
        self.ollama_model.clear()
        self.ollama_vision_model.clear()
        
        models = ollama_client.list_models()
        if models:
            for model in models:
                model_name = model.get("name", "")
                if model_name:
                    self.ollama_model.addItem(model_name)
                    self.ollama_vision_model.addItem(model_name)
        else:
            self.ollama_model.addItem("llama3.2:latest")
            self.ollama_vision_model.addItem("llava:latest")

    def _load_settings(self):
        self.ollama_url.setText(config.get("ollama.base_url", "http://localhost:11434"))
        
        current_model = config.get("ollama.model", "llama3.2:latest")
        idx = self.ollama_model.findText(current_model)
        if idx >= 0:
            self.ollama_model.setCurrentIndex(idx)
        
        vision_model = config.get("ollama.vision_model", "llava:latest")
        idx = self.ollama_vision_model.findText(vision_model)
        if idx >= 0:
            self.ollama_vision_model.setCurrentIndex(idx)

        self.ollama_timeout.setValue(config.get("ollama.timeout", 120))
        self.ollama_temperature.setValue(config.get("ollama.temperature", 0.7))

        self.hotkey_prompt.setText(config.get("hotkeys.prompt_panel", "ctrl+p"))
        self.hotkey_text.setText(config.get("hotkeys.text_processing", "ctrl+e"))

        self.agent_update_freq.setValue(config.get("agent.update_frequency", 1.0))
        self.agent_max_history.setValue(config.get("agent.max_history", 100))
        
        log_level = config.get("agent.log_level", "INFO")
        idx = self.agent_log_level.findText(log_level)
        if idx >= 0:
            self.agent_log_level.setCurrentIndex(idx)
        
        self.agent_autostart.setChecked(config.get("agent.auto_start", False))

        self.security_confirm_delete.setChecked(
            config.get("security.require_confirmation_for_delete", True)
        )
        self.security_confirm_execute.setChecked(
            config.get("security.require_confirmation_for_execute", True)
        )

        self.gui_opacity.setValue(config.get("gui.opacity", 0.95))
        self.gui_font_size.setValue(config.get("gui.font_size", 12))
        self.gui_animation.setValue(config.get("gui.animation_duration", 200))

    def _save_settings(self):
        config.set("ollama.base_url", self.ollama_url.text())
        config.set("ollama.model", self.ollama_model.currentText())
        config.set("ollama.vision_model", self.ollama_vision_model.currentText())
        config.set("ollama.timeout", self.ollama_timeout.value())
        config.set("ollama.temperature", self.ollama_temperature.value())

        config.set("hotkeys.prompt_panel", self.hotkey_prompt.text())
        config.set("hotkeys.text_processing", self.hotkey_text.text())

        config.set("agent.update_frequency", self.agent_update_freq.value())
        config.set("agent.max_history", self.agent_max_history.value())
        config.set("agent.log_level", self.agent_log_level.currentText())
        config.set("agent.auto_start", self.agent_autostart.isChecked())

        config.set("security.require_confirmation_for_delete", self.security_confirm_delete.isChecked())
        config.set("security.require_confirmation_for_execute", self.security_confirm_execute.isChecked())

        config.set("gui.opacity", self.gui_opacity.value())
        config.set("gui.font_size", self.gui_font_size.value())
        config.set("gui.animation_duration", self.gui_animation.value())

        self.logger.info("Settings saved")

    def _reset_settings(self):
        config.config = config.DEFAULT_CONFIG.copy()
        config.save()
        self._load_settings()
        self.logger.info("Settings reset to defaults")
