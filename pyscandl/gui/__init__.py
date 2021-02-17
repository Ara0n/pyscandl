from .main_window import MainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication([])
pyscandl_qt = MainWindow()
exit(app.exec())
