import contextlib

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThreadPool, pyqtSignal, QThread

from .worker import Worker
from .. import Pyscandl
from ..modules.autodl import Controller
from ..modules.fetchers import FetcherEnum


class QStdoutText(QTextEdit):
    _write = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self._write.connect(self.new_text)

    def write(self, txt):
        self._write.emit(txt)

    def new_text(self, txt):
        bottom = self.verticalScrollBar().value() == self.verticalScrollBar().maximum()
        self.insertPlainText(str(txt))
        if bottom:
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def flush(self):
        pass



class MainWindow(QMainWindow):
    _autodl_progress_count = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threadpool = QThreadPool()
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
        edit_button.clicked.connect(self._edit_dialog)
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
        panel = QWidget()
        layout = QVBoxLayout()

        # constructing the form
        param_line = QHBoxLayout()
        param_line.addLayout(self._folder_widget("Save location:"))
        quiet = QCheckBox("quiet")
        param_line.addWidget(quiet)
        tiny = QCheckBox("tiny")
        tiny.setToolTip("don't write the manga name in the title (useful if using ebook libraries)")
        param_line.addWidget(tiny)
        layout.addLayout(param_line)
        mode = QComboBox()
        mode.addItem("PDF", (True, False, False))
        mode.addItem("image", (False, False, True))
        mode.addItem("keep", (False, True, False))
        mode.setToolTip("""- pdf: downloads only the pdf of the manga
- keep: downloads the pdf but also keep the images in a chapter subfolder
- image: downloads only the images in a chapter subfolder and don't create the pdf""")
        param_line.addWidget(mode)

        # progress bar
        self._autodl_progress = QProgressBar()
        self._autodl_progress_count.connect(self._autodl_progress.setValue)
        layout.addWidget(self._autodl_progress)

        # output
        self._autodl_out = QStdoutText()
        layout.addWidget(self._autodl_out)

        # launching actions
        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignRight)
        download = QPushButton("Download")
        download.clicked.connect(self._worker_autodl_download)
        download.clicked.connect(self._autodl_out.clear)
        buttons.addWidget(download)
        scan = QPushButton("Scan")
        scan.setToolTip("checks if there is any new chapters but doesn't download them")
        scan.clicked.connect(self._worker_autodl_scan)
        scan.clicked.connect(self._autodl_out.clear)
        buttons.addWidget(scan)
        layout.addLayout(buttons)

        panel.setLayout(layout)
        return panel

    def _autodl_download(self, sender):
        parent = sender.parent()
        pdf, keep, image = parent.findChild(QComboBox).currentData()
        output = parent.findChild(QLineEdit).text()
        quiet, tiny = [bool(check.checkState()) for check in parent.findChildren(QCheckBox)]
        controller = Controller(
            output=output if output else ".",
            quiet=quiet,
            tiny=tiny
        )
        mangas = controller.list_mangas(format=False)
        self._autodl_progress.setMaximum(len(mangas))
        with contextlib.redirect_stdout(self._autodl_out):
            for manga in mangas:
                self._autodl_progress_count.emit(self._autodl_progress.value() + 1)
                controller.scan(manga)
                controller.download(manga, pdf, keep, image)
            controller.save()
            self._autodl_progress_count.emit(self._autodl_progress.value() + 1)
        if not quiet:
            self._autodl_out.write(f"{controller.downloads} chapters downloaded")

    def _worker_autodl_download(self):
        self._autodl_progress.reset()
        buttons = self.sender().parent().findChildren(QPushButton)[1:]
        buttons[0].setDisabled(True)
        buttons[1].setDisabled(True)
        print("starting dl")
        worker = Worker(self._autodl_download, self.sender())
        worker.signals.result.connect(lambda x: print(x))
        worker.signals.finished.connect(lambda: print("finished"))
        worker.signals.finished.connect(buttons[0].setEnabled)
        worker.signals.finished.connect(buttons[1].setEnabled)

        self._threadpool.start(worker)


    def _autodl_scan(self):
        controller = Controller()
        mangas = controller.list_mangas(format=False)
        self._autodl_progress.setMaximum(len(mangas))
        with contextlib.redirect_stdout(self._autodl_out):
            for manga in mangas:
                self._autodl_progress_count.emit(self._autodl_progress.value() + 1)
                controller.scan(manga)
            self._autodl_progress_count.emit(self._autodl_progress.value() + 1)

    def _worker_autodl_scan(self):
        self._autodl_progress.reset()
        buttons = self.sender().parent().findChildren(QPushButton)[1:]
        buttons[0].setDisabled(True)
        buttons[1].setDisabled(True)
        print("starting dl")
        worker = Worker(self._autodl_scan)
        worker.signals.result.connect(lambda x: print(x))
        worker.signals.finished.connect(lambda: print("finished"))
        worker.signals.finished.connect(buttons[0].setEnabled)
        worker.signals.finished.connect(buttons[1].setEnabled)

        self._threadpool.start(worker)

    def manual_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        top_layout = QGridLayout()

        # constructing 2 line form in the QGridLayout
        ## first line: save location, quiet, tiny, download mode
        first_line = QHBoxLayout()
        first_line.addLayout(self._folder_widget("Save location:"))
        quiet = QCheckBox("quiet")
        first_line.addWidget(quiet)
        tiny = QCheckBox("tiny")
        tiny.setToolTip("don't write the manga name in the title (useful if using ebook libraries)")
        first_line.addWidget(tiny)
        mode = QComboBox()
        mode.addItem("PDF", (True, False, False))
        mode.addItem("image", (False, False, True))
        mode.addItem("keep", (False, True, False))
        mode.setToolTip("""- pdf: downloads only the pdf of the manga
- keep: downloads the pdf but also keep the images in a chapter subfolder
- image: downloads only the images in a chapter subfolder and don't create the pdf""")
        first_line.addWidget(mode)

        ## second line: fetcher, link, starting point, end mode, end point
        second_line = QHBoxLayout()
        second_line.addWidget(QLabel("Fetcher:"))
        fetchers = QComboBox()
        for fetcher in FetcherEnum.list():
            fetchers.addItem(fetcher, FetcherEnum.get(fetcher))
        second_line.addWidget(fetchers)
        second_line.addWidget(QLabel("Link:"))
        second_line.addWidget(QLineEdit())
        all = QCheckBox("all")
        second_line.addWidget(all)
        second_line.addWidget(QLabel("Start:"))
        start = QDoubleSpinBox()
        start.setMaximum(2147483647)
        start.setValue(1)
        second_line.addWidget(start)
        second_line.addWidget(QLabel("Stop:"))
        end_mode = QComboBox()
        end_mode.addItem("count chapters", True)
        end_mode.addItem("last chapter", False)
        end_mode.setToolTip("""- count chapters: once the total number of chapters downloaded equals the specified number
        - last chapter: once the chapter downloaded equals or exceeds the the specifed number""")
        second_line.addWidget(end_mode)
        stop = QDoubleSpinBox()
        stop.setMaximum(2147483647)
        stop.setValue(1)
        second_line.addWidget(stop)
        all.stateChanged.connect(end_mode.setDisabled)
        all.stateChanged.connect(stop.setDisabled)

        # output
        self._manual_out = QStdoutText()

        # launching actions
        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignRight)
        download = QPushButton("Download")
        download.clicked.connect(self._worker_manual_download)
        buttons.addWidget(download)
        cancel = QPushButton("Cancel")
        buttons.addWidget(cancel)

        # building the layout
        layout.addLayout(first_line)
        layout.addLayout(second_line)
        layout.addWidget(self._manual_out)
        layout.addLayout(buttons)
        panel.setLayout(layout)
        return panel

    def _manual_download(self, sender):
        parent = sender.parent()
        quiet, tiny, all = [bool(check.checkState()) for check in parent.findChildren(QCheckBox)]
        output, link = [line_ed.text() for line_ed in parent.findChildren(QLineEdit)[:2]]
        start, stop = [int(spin.value()) if spin.value() == int(spin.value()) else spin.value() for spin in parent.findChildren(QDoubleSpinBox)]
        dl_mode, fetcher, stop_mode = [combo.currentData() for combo in parent.findChildren(QComboBox)]
        manual_dl = Pyscandl(
            fetcher=fetcher,
            chapstart=start,
            output=output if output != "" else ".",
            link=link,
            all=all,
            pdf=dl_mode[0],
            keep=dl_mode[1],
            image=dl_mode[2],
            download_number=stop if stop_mode else 1,
            chapend=stop if not stop_mode else 0,
            quiet=quiet,
            tiny=tiny
        )

        with contextlib.redirect_stdout(self._manual_out):
            manual_dl.full_download()

    def _worker_manual_download(self):
        self.sender().setDisabled(True)
        print("starting dl")
        worker = Worker(self._manual_download, self.sender())
        worker.signals.result.connect(lambda x: print(x))
        worker.signals.finished.connect(lambda: print("finished"))
        worker.signals.finished.connect(self.sender().setEnabled)

        self._threadpool.start(worker)

    def _folder_widget(self, label=""):
        folder_widget = QHBoxLayout()
        if label:
            folder_widget.addWidget(QLabel(label))
        path = QLineEdit()
        file_button = QPushButton(QFileIconProvider().icon(QFileIconProvider.Folder), "")
        file_button.clicked.connect(self._folder_select)
        folder_widget.addWidget(path)
        folder_widget.addWidget(file_button)
        return folder_widget

    def _folder_select(self):
        sender = self.sender()
        folder_select = QFileDialog()
        folder_select.setFileMode(QFileDialog.DirectoryOnly)
        folder_select.fileSelected.connect(sender.parent().findChild(QLineEdit).setText)
        folder_select.exec()

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
            self._error_popups(
                icon=QMessageBox.Critical,
                title="name error",
                text="an error when entering the link was detected:",
                info_text="please enter a link for the new manga"
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
                self._error_popups(
                    icon=QMessageBox.Critical,
                    title="chapter list error",
                    text="an error when entering the chapters was detected:",
                    info_text="please only type chapter numbers like 23, 0 or 2.3 separated only by spaces or carriage returns",
                    detailed_text=str(e))
                sender.parent().reject()

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
