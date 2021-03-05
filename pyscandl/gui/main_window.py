from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import *

from .panels.autodl import QAutodl
from .panels.manga import QManga
from .panels.manual import QManual


class MainWindow(QMainWindow):
    _autodl_progress_count = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()
        self.show()

    def setupUi(self):
        self.setWindowTitle("pyscandl")
        tabs = QTabWidget()
        manga_panel = QManga()
        autodl_panel = QAutodl()
        manual_panel = QManual()
        tabs.addTab(manga_panel, "&manga")
        tabs.addTab(autodl_panel, "&autodl")
        tabs.addTab(manual_panel, "ma&nual")
        self.setCentralWidget(tabs)
