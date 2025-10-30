from PyQt5.QtWidgets import QMainWindow, QTabWidget

from ui.lore_tab import LoreTab
from ui.characters_tab import CharactersTab
from ui.quests_tab import EventsTab
from ui.dialogues_tab import DialoguesTab
from ui.settings_tab import SettingsTab


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Dinov AI Tools")
        self.setMinimumSize(1000, 700)

        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)

        self.lore_tab = LoreTab()
        self.tabs.addTab(self.lore_tab, "Лор")

        self.characters_tab = CharactersTab()
        self.tabs.addTab(self.characters_tab, "Персонажи")

        self.quests_tab = EventsTab()
        self.tabs.addTab(self.quests_tab, "Квесты и события")

        self.dialogues_tab = DialoguesTab()
        self.tabs.addTab(self.dialogues_tab, "Диалоги")

        self.settings_tab = SettingsTab()
        self.tabs.addTab(self.settings_tab, "Настройки")

        self.tabs.currentChanged.connect(self.on_tab_changed)

        self.characters_tab.characters_updated.connect(self.on_characters_updated)

    def on_tab_changed(self, index: int) -> None:
        if index == 1:
            self.characters_tab.load_characters()
        elif index == 2:
            self.quests_tab.load_events()
            self.quests_tab.refresh_characters()
        elif index == 3:
            self.dialogues_tab.load_characters()

    def on_characters_updated(self) -> None:
        self.quests_tab.refresh_characters()
        self.dialogues_tab.load_characters()
