from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from ..modules.autodl import Controller
from ..modules.fetchers import FetcherEnum


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
        new_button.clicked.connect(self._create_dialog)
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
        if current[4]:
            self._form.addRow("- number of chapters downloaded:", QLabel(str(len(current[4]))))
            self._form.addRow("- last chapter:", QLabel(str(current[4][0])))
        else:
            self._form.addRow("- number of chapters downloaded:", QLabel("no chapters downloaded yet"))
            self._form.addRow("- last chapter:", QLabel("no chapters downloaded yet"))


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

    def _create_dialog(self):
        create = QDialog()
        layout = QVBoxLayout()
        form = QFormLayout()

        # info form
        form.addRow("Name:", QLineEdit())
        form.addRow("Link:", QLineEdit())
        fetchers = QComboBox()
        fetchers.addItems(FetcherEnum.list(standalone=False))
        form.addRow("Fetcher:", fetchers)
        form.addRow("Chapters (optional):", QTextEdit())
        form.addRow("Archived ?", QCheckBox())

        # accept and cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._create_save)
        buttons.accepted.connect(create.accept)
        buttons.rejected.connect(create.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        create.setLayout(layout)
        create.exec()

    def _create_save(self):
        sender = self.sender()
        form = sender.parent().layout().itemAt(0)
        name = form.itemAt(1).widget().text()
        link = form.itemAt(3).widget().text()
        if not name:
            self._error_popups(
                icon=QMessageBox.Critical,
                title="name error",
                text="an error when entering the name was detected:",
                info_text="please enter a name for the new manga"
            )
            sender.parent().reject()
        elif not link:
            self._error_popups(
                icon=QMessageBox.Critical,
                title="name error",
                text="an error when entering the link was detected:",
                info_text="please enter a link for the new manga"
            )
            sender.parent().reject()
        else:
            fetcher = form.itemAt(5).widget().currentText()
            archived = form.itemAt(9).widget().isChecked()
            try:
                chaps = [float(chap) if "." in chap else int(chap) for chap in form.itemAt(7).widget().toPlainText().replace("\n", " ").split(" ") if chap != ""]

                self._controller.add(name, link, fetcher, chaps, archived)
                self._controller.save()
                self._mangas.addItem(name)
            except ValueError as e:
                # setting up the error message box
                self._error_popups(
                    icon=QMessageBox.Critical,
                    title="chapter list error",
                    text="an error when entering the chapters was detected:",
                    info_text="please only type chapter numbers like 23, 0 or 2.3 separated only by spaces or carriage returns",
                    detailed_text=str(e))
                sender.parent().reject()

    def _update_info(self):
        sender = self.sender()
        current = self._controller.manga_info(sender.currentText())
        self._form.itemAt(1).widget().setText(current[2])
        self._form.itemAt(3).widget().setText(current[1])
        self._form.itemAt(5).widget().setText("YES" if current[3] else "NO")
        if current[4]:
            self._form.itemAt(7).widget().setText(str(len(current[4])))
            self._form.itemAt(9).widget().setText(str(current[4][0]))
        else:
            self._form.itemAt(7).widget().setText("no chapters downloaded yet")
            self._form.itemAt(9).widget().setText("no chapters downloaded yet")

    def _error_popups(self, icon=QMessageBox.Critical, title="error", text=None, info_text=None, detailed_text=None):
        error = QMessageBox()
        error.setIcon(icon)
        error.setWindowTitle(title)
        if text:
            error.setText(text)
        if info_text:
            error.setInformativeText(info_text)
        if detailed_text:
            error.setDetailedText(detailed_text)
        error.exec()
