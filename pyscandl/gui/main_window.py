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
        panel = QWidget()
        layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        # setting up the list of mangas
        self._mangas = QComboBox()
        self._mangas.addItems(self._controller.list_mangas(all=True, format=False))
        current = self._controller.manga_info(self._mangas.currentText())
        top_layout.addWidget(self._mangas)
        self._mangas.currentTextChanged.connect(self._update_info)

        # setting up the control pane
        see_chaps_button = QPushButton("see all chapters")
        see_chaps_button.clicked.connect(self._chapter_list_message)
        new_button = QPushButton("new")
        edit_button = QPushButton("edit")
        delete_button = QPushButton("delete")
        delete_button.clicked.connect(self._delete_confirm)
        top_layout.addWidget(see_chaps_button)
        top_layout.addWidget(new_button)
        top_layout.addWidget(edit_button)
        top_layout.addWidget(delete_button)

        # setting up the info pane
        bottom = QGroupBox()
        bottom.setTitle("info")
        self._form = QFormLayout()
        bottom.setLayout(self._form)
        self._form.addRow("- link:", QLabel(current[2]))
        self._form.addRow("- fetcher:", QLabel(current[1]))
        self._form.addRow("- archived:", QLabel("YES" if current[3] else "NO"))
        self._form.addRow("- number of chapters downloaded:", QLabel(str(len(current[4]))))
        self._form.addRow("- last chapter:", QLabel(str(current[4][0])))

        # adding everything to the pannel
        layout.addLayout(top_layout)
        layout.addWidget(bottom)
        panel.setLayout(layout)
        return panel

    def autodl_panel(self):
        return QWidget()

    def manual_panel(self):
        return QWidget()

    def _chapter_list_message(self):
        # setting up the chapterlist message box
        chaplist = QMessageBox()
        chaplist.setIcon(QMessageBox.Information)
        chaplist.setWindowTitle("chapter list")
        chaplist.setText(f"chapter list for {self._mangas.currentText()}:")
        chaplist.setInformativeText(" ".join([str(chap) for chap in self._controller.manga_info(self._mangas.currentText())[4]]))
        chaplist.exec()

    def _delete_confirm(self):
        delete_msg = QMessageBox.question(self, "deleting manga", f"are you sure you want to delete {self._mangas.currentText()}", QMessageBox.Yes, QMessageBox.No)

        if delete_msg == QMessageBox.Yes:
            self._controller.delete_manga(self._mangas.currentText())
            self._controller.save()
            self._mangas.removeItem(self._mangas.currentIndex())

    def _update_info(self):
        sender = self.sender()
        current = self._controller.manga_info(sender.currentText())
        self._form.itemAt(1).widget().setText(current[2])
        self._form.itemAt(3).widget().setText(current[1])
        self._form.itemAt(5).widget().setText("YES" if current[3] else "NO")
        self._form.itemAt(7).widget().setText(str(len(current[4])))
        self._form.itemAt(9).widget().setText(str(current[4][0]))