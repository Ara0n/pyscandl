from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from ..modules.autodl import Controller


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._controller = Controller()
        self.setupUi()
        self.show()

    def setupUi(self):
        self.setWindowTitle("pyscandl")
        tabs = QTabWidget()
        manga_panel = self.manga_panel()
        autodl_panel = self.autodl_panel()
        manual_panel = self.manual_panel()
        tabs.addTab(manga_panel, "&manga")
        tabs.addTab(autodl_panel, "&autodl")
        tabs.addTab(manual_panel, "ma&nual")
        self.setCentralWidget(tabs)

    def manga_panel(self):
        return QWidget()

    def autodl_panel(self):
        return QWidget()

    def manual_panel(self):
        return QWidget()
