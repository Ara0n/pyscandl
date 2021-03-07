from PyQt5.QtWidgets import *

from ..custom_elements import QErrorPopup
from ...modules.autodl import Controller
from ...modules.fetchers import FetcherEnum


class QManga(QWidget):
    def __init__(self):
        super().__init__()
        self._controller = Controller()
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        top_layout = QHBoxLayout()

        # setting up the list of mangas
        self._mangas = QComboBox()
        self._mangas.addItems(self._controller.list_mangas(all=True, format=False))
        current = self._controller.manga_info(self._mangas.currentText())
        top_layout.addWidget(self._mangas)
        self._mangas.currentTextChanged.connect(self._update_info)

        # setting up the control pane
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_info)
        see_chaps_button = QPushButton("see all chapters")
        see_chaps_button.clicked.connect(self._chapter_list_message)
        new_button = QPushButton("new")
        new_button.clicked.connect(self._create_dialog)
        edit_button = QPushButton("edit")
        edit_button.clicked.connect(self._edit_dialog)
        edit_button.setEnabled(bool(current))
        self._mangas.currentTextChanged.connect(lambda x: edit_button.setEnabled(bool(x)))
        delete_button = QPushButton("delete")
        delete_button.setEnabled(bool(current))
        delete_button.clicked.connect(self._delete_confirm)
        self._mangas.currentTextChanged.connect(lambda x: delete_button.setEnabled(bool(x)))
        top_layout.addWidget(refresh_button)
        top_layout.addWidget(see_chaps_button)
        top_layout.addWidget(new_button)
        top_layout.addWidget(edit_button)
        top_layout.addWidget(delete_button)

        # setting up the info pane
        bottom = QGroupBox()
        bottom.setTitle("info")
        self._form = QFormLayout()
        bottom.setLayout(self._form)
        self._form.addRow("- link:", QLabel(current[2] if current is not None else ""))
        self._form.addRow("- fetcher:", QLabel(current[1] if current is not None else ""))
        self._form.addRow("- archived:", QLabel(("YES" if current[3] else "NO") if current is not None else ""))
        if current is not None and current[4]:
            self._form.addRow("- number of chapters downloaded:", QLabel(str(len(current[4])) if current is not None else ""))
            self._form.addRow("- last chapter:", QLabel(str(current[4][0]) if current is not None else ""))
        else:
            self._form.addRow("- number of chapters downloaded:", QLabel("no chapters downloaded yet" if current is not None else ""))
            self._form.addRow("- last chapter:", QLabel("no chapters downloaded yet" if current is not None else ""))

        # adding everything to the pannel
        layout.addLayout(top_layout)
        layout.addWidget(bottom)

    def _update_info(self):
        if self._mangas.currentText():
            current = self._controller.manga_info(self._mangas.currentText())
            self._form.itemAt(1).widget().setText(current[2])
            self._form.itemAt(3).widget().setText(current[1])
            self._form.itemAt(5).widget().setText("YES" if current[3] else "NO")
            if current[4]:
                self._form.itemAt(7).widget().setText(str(len(current[4])))
                self._form.itemAt(9).widget().setText(str(current[4][0]))
            else:
                self._form.itemAt(7).widget().setText("no chapters downloaded yet")
                self._form.itemAt(9).widget().setText("no chapters downloaded yet")

    def _chapter_list_message(self):
        # setting up the chapterlist message box
        chaplist = QMessageBox()
        chaplist.setIcon(QMessageBox.Information)
        chaplist.setWindowTitle("chapter list")
        chaplist.setText(f"chapter list for {self._mangas.currentText()}:")
        chaplist.setInformativeText(" ".join([str(chap) for chap in self._controller.manga_info(self._mangas.currentText())[4]]))
        chaplist.exec()

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
            QErrorPopup(
                icon=QMessageBox.Critical,
                title="name error",
                text="an error when entering the name was detected:",
                info_text="please enter a name for the new manga"
            )
            sender.parent().reject()
        elif not link:
            QErrorPopup(
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
                QErrorPopup(
                    icon=QMessageBox.Critical,
                    title="chapter list error",
                    text="an error when entering the chapters was detected:",
                    info_text="please only type chapter numbers like 23, 0 or 2.3 separated only by spaces or carriage returns",
                    detailed_text=str(e)
                )
                sender.parent().reject()

    def _edit_dialog(self):
        create = QDialog()
        layout = QVBoxLayout()
        form = QFormLayout()
        manga = self._controller.manga_info(self._mangas.currentText())

        # info form
        link = QLineEdit()
        link.setText(manga[2])
        form.addRow("Link:", link)
        fetchers = QComboBox()
        fetchers.addItems(FetcherEnum.list(standalone=False))
        fetchers.setCurrentIndex(fetchers.findText(manga[1]))
        form.addRow("Fetcher:", fetchers)
        mode = QComboBox()
        mode.addItems(["set", "add", "delete"])
        mode.setToolTip("""- set: set the listed chapters as the chapters stored
- add: add the listed chapters to the chapters stored
- delete: delete the listed chapters from the chapters stored""")
        form.addRow("Chapter mode:", mode)
        chaps = QTextEdit()
        chaps.setText(" ".join([str(chap) for chap in manga[4]]))
        form.addRow("Chapters:", chaps)
        archived = QCheckBox()
        archived.setChecked(manga[3])
        form.addRow("Archived ?", archived)

        # accept and cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._edit_save)
        buttons.accepted.connect(create.accept)
        buttons.rejected.connect(create.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)
        create.setLayout(layout)
        create.exec()

    def _edit_save(self):
        sender = self.sender()
        form = sender.parent().layout().itemAt(0)
        link = form.itemAt(1).widget().text()
        if not link:
            QErrorPopup(
                icon=QMessageBox.Critical,
                title="name error",
                text="an error when entering the link was detected:",
                info_text="please enter a link for the manga"
            )
            sender.parent().reject()
        else:
            fetcher = form.itemAt(3).widget().currentText()
            archived = form.itemAt(9).widget().isChecked()
            try:
                chaps = [float(chap) if "." in chap else int(chap) for chap in
                         form.itemAt(7).widget().toPlainText().replace("\n", " ").split(" ") if chap != ""]

                mode = form.itemAt(5).widget().currentText()
                if mode == "set":
                    old_chaps = self._controller.manga_info(self._mangas.currentText())[4]
                    self._controller.rm_chaps(self._mangas.currentText(), [str(chap) for chap in old_chaps])
                    self._controller.edit(self._mangas.currentText(), link, fetcher, chaps, archived)
                elif mode == "add":
                    self._controller.edit(self._mangas.currentText(), link, fetcher, chaps, archived)
                elif mode == "delete":
                    self._controller.rm_chaps(self._mangas.currentText(), [str(chap) for chap in chaps])
                    self._controller.edit(self._mangas.currentText(), link, fetcher, None, archived)
                self._controller.save()
                self._update_info()
            except ValueError as e:
                # setting up the error message box
                QErrorPopup(
                    icon=QMessageBox.Critical,
                    title="chapter list error",
                    text="an error when entering the chapters was detected:",
                    info_text="please only type chapter numbers like 23, 0 or 2.3 separated only by spaces or carriage returns",
                    detailed_text=str(e)
                )
                sender.parent().reject()

    def _delete_confirm(self):
        delete_msg = QMessageBox.question(self, "deleting manga", f"are you sure you want to delete {self._mangas.currentText()}", QMessageBox.Yes, QMessageBox.No)

        if delete_msg == QMessageBox.Yes:
            self._controller.delete_manga(self._mangas.currentText())
            self._controller.save()
            self._mangas.removeItem(self._mangas.currentIndex())

    def _refresh_info(self):
        self._mangas.clear()
        self._mangas.addItems(self._controller.list_mangas(all=True, format=False))
