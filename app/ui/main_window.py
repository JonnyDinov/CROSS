from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QTabWidget,
    QFileDialog,
    QMessageBox,
    QAction,
    QDockWidget,
    QTextEdit,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
)

from app.core.database import Database
from app.core.memory import MemoryStore, MemoryRecord
from app.core.ollama import OllamaClient
from app.services.world_service import WorldService
from app.services.prompt_builder import PromptBuilder
from app.exporters.export_manager import ExportManager
from app.exporters.pdf_exporter import PDFExporter
from app.ui.tabs.characters import CharactersTab
from app.ui.tabs.lore import LoreTab
from app.ui.tabs.events import EventsTab
from app.ui.tabs.scenes import ScenesTab
from app.ui.tabs.templates import TemplatesTab
from app.ui.tabs.quests import QuestsTab
from app.ui.components.relationship_graph import RelationshipGraph
from app.ui.styles import DARK_THEME_STYLE
from app.utils.dice import DiceRoller


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("World Builder with Ollama")
        self.resize(1400, 900)

        self.db_path = "world_editor.db"
        self.db = Database(self.db_path)
        self.ollama = OllamaClient(
            base_url=self.db.get_setting("ollama_base_url", "http://localhost:11434"),
            model=self.db.get_setting("ollama_model", "llama3"),
        )
        self.memory_store = MemoryStore("memory.db", self.ollama)
        self.world_service = WorldService(self.db, self.memory_store)
        self.prompt_builder = PromptBuilder(self.db, self.memory_store)
        self.export_manager = ExportManager(self.db)
        self.pdf_exporter = PDFExporter()

        self.tabs = QTabWidget()
        self.characters_tab = CharactersTab(self.world_service, self.ollama, on_change=self.rebuild_graph)
        self.lore_tab = LoreTab(self.world_service, self.ollama, on_change=self.rebuild_graph)
        self.scenes_tab = ScenesTab(self.world_service, self.ollama, self.prompt_builder, on_change=self.rebuild_graph)
        self.events_tab = EventsTab(self.world_service, self.ollama, on_change=self.rebuild_graph)
        self.templates_tab = TemplatesTab(self.world_service, self.ollama, on_change=self.rebuild_graph)
        self.quests_tab = QuestsTab(self.world_service, self.ollama)

        self.tabs.addTab(self.lore_tab, "Лор")
        self.tabs.addTab(self.characters_tab, "Персонажи")
        self.tabs.addTab(self.scenes_tab, "Сцены")
        self.tabs.addTab(self.events_tab, "Ивенты")
        self.tabs.addTab(self.templates_tab, "Шаблоны")
        self.tabs.addTab(self.quests_tab, "Квесты")

        container = QWidget()
        layout = self.tabs
        container.setLayout(None)
        self.setCentralWidget(self.tabs)

        self._init_menu()
        self._init_graph_dock()
        self._init_dice_dock()

        self.setStyleSheet(DARK_THEME_STYLE)
        self.rebuild_graph()

    def _init_menu(self):
        menu = self.menuBar()

        file_menu = menu.addMenu("Файл")
        export_action = QAction("Экспорт мира (JSON)", self)
        export_action.triggered.connect(self.export_world)
        import_action = QAction("Импорт мира (JSON)", self)
        import_action.triggered.connect(self.import_world)
        file_menu.addAction(export_action)
        file_menu.addAction(import_action)

        export_scene_action = QAction("Экспорт сцены (Markdown)", self)
        export_scene_action.triggered.connect(self.export_scene_markdown)
        export_character_action = QAction("Экспорт персонажа (Markdown)", self)
        export_character_action.triggered.connect(self.export_character_markdown)
        export_pdf_scene_action = QAction("Экспорт сцены (PDF)", self)
        export_pdf_scene_action.triggered.connect(self.export_scene_pdf)
        export_pdf_character_action = QAction("Экспорт персонажа (PDF)", self)
        export_pdf_character_action.triggered.connect(self.export_character_pdf)

        export_menu = menu.addMenu("Экспорт")
        export_menu.addAction(export_scene_action)
        export_menu.addAction(export_character_action)
        export_menu.addSeparator()
        export_menu.addAction(export_pdf_scene_action)
        export_menu.addAction(export_pdf_character_action)

        settings_menu = menu.addMenu("Настройки")
        settings_action = QAction("Настройки Ollama", self)
        settings_action.triggered.connect(self.configure_ollama)
        settings_menu.addAction(settings_action)

    def _init_graph_dock(self):
        from PyQt5.QtWidgets import QVBoxLayout, QWidget
        dock = QDockWidget("Карта связей", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        dock_widget = QWidget()
        dock_layout = QVBoxLayout()
        
        self.graph_view = RelationshipGraph()
        self.refresh_graph_btn = QPushButton("Обновить граф")
        self.refresh_graph_btn.clicked.connect(self.rebuild_graph)
        
        dock_layout.addWidget(self.refresh_graph_btn)
        dock_layout.addWidget(self.graph_view)
        dock_widget.setLayout(dock_layout)
        dock.setWidget(dock_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        self.graph_view.scene.selectionChanged.connect(self._on_graph_selection)

    def _init_dice_dock(self):
        dock = QDockWidget("Дайс-роллер", self)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        widget = QWidget()
        layout = QVBoxLayout()
        self.dice_input = QLineEdit()
        self.dice_input.setPlaceholderText("2d6+3")
        self.dice_button = QPushButton("Бросить")
        self.dice_result = QLabel("Результат")

        layout.addWidget(self.dice_input)
        layout.addWidget(self.dice_button)
        layout.addWidget(self.dice_result)
        widget.setLayout(layout)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

        self.dice_button.clicked.connect(self.roll_dice)

    def roll_dice(self):
        expression = self.dice_input.text() or "1d20"
        try:
            total, rolls = DiceRoller.roll(expression)
            self.dice_result.setText(f"{total} ({rolls})")
        except Exception as e:
            QMessageBox.warning(self, "Дайс-роллер", f"Ошибка: {e}")

    def configure_ollama(self):
        dialog = QFileDialog(self)
        # Placeholder for actual settings dialog
        QMessageBox.information(self, "Настройки Ollama", "Конфигурация в разработке")

    def export_world(self):
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт мира", "world.json", "JSON (*.json)")
        if not path:
            return
        self.export_manager.export_world_json(path)
        QMessageBox.information(self, "Экспорт", "Мир успешно экспортирован")

    def import_world(self):
        path, _ = QFileDialog.getOpenFileName(self, "Импорт мира", "", "JSON (*.json)")
        if not path:
            return
        self.export_manager.import_world_json(path)
        self.characters_tab.refresh()
        self.lore_tab.refresh()
        self.events_tab.refresh()
        self.scenes_tab.refresh()
        self.templates_tab.refresh()
        self.quests_tab.refresh()
        QMessageBox.information(self, "Импорт", "Мир успешно импортирован")

    def export_scene_markdown(self):
        scene = self.scenes_tab.scene_list.currentItem()
        if not scene:
            QMessageBox.warning(self, "Экспорт", "Выберите сцену")
            return
        scene_data = scene.data( Qt.UserRole)
        messages = self.world_service.list_scene_messages(scene_data.id)
        entries = [(msg.speaker, msg.content) for msg in messages]
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт сцены", f"{scene_data.title}.md", "Markdown (*.md)")
        if not path:
            return
        self.export_manager.export_scene_markdown(scene_data, entries, path)
        QMessageBox.information(self, "Экспорт", "Сцена экспортирована в Markdown")

    def export_character_markdown(self):
        item = self.characters_tab.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Экспорт", "Выберите персонажа")
            return
        character = item.data(Qt.UserRole)
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт персонажа", f"{character.name}.md", "Markdown (*.md)")
        if not path:
            return
        self.export_manager.export_character_markdown(character, path)
        QMessageBox.information(self, "Экспорт", "Персонаж экспортирован в Markdown")

    def export_scene_pdf(self):
        item = self.scenes_tab.scene_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Экспорт", "Выберите сцену")
            return
        scene = item.data(Qt.UserRole)
        messages = self.world_service.list_scene_messages(scene.id)
        entries = [(msg.speaker, msg.content) for msg in messages]
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт сцены", f"{scene.title}.pdf", "PDF (*.pdf)")
        if not path:
            return
        self.pdf_exporter.export_scene(scene, entries, path)
        QMessageBox.information(self, "Экспорт", "Сцена экспортирована в PDF")

    def export_character_pdf(self):
        item = self.characters_tab.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Экспорт", "Выберите персонажа")
            return
        character = item.data(Qt.UserRole)
        path, _ = QFileDialog.getSaveFileName(self, "Экспорт персонажа", f"{character.name}.pdf", "PDF (*.pdf)")
        if not path:
            return
        self.pdf_exporter.export_character(character, path)
        QMessageBox.information(self, "Экспорт", "Персонаж экспортирован в PDF")

    def rebuild_graph(self):
        characters = self.world_service.list_characters()
        nodes = [c.name for c in characters]
        edges = {}
        for character in characters:
            related = [name.strip() for name in character.relationships.split(",") if name.strip()]
            edges[character.name] = [r for r in related if r in nodes]
        self.graph_view.build_graph(nodes, edges)

    def _on_graph_selection(self):
        label = self.graph_view.selected_node_label()
        if not label:
            return
        facts = self.memory_store.get_semantic_facts(label, limit=5)
        if facts:
            details = "\n".join(f"- {fact.content}" for fact in facts)
            QMessageBox.information(self, label, details)
        else:
            QMessageBox.information(self, label, "Нет данных")
