import contextlib

from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal
from PyQt5.QtWidgets import *

from .custom_elements import QFolderSelect, QStdoutText
from .panels.manga import QManga
from .panels.manual import QManual
from .worker import Worker
from ..modules.autodl import Controller


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
        manga_panel = QManga()
        autodl_panel = self.autodl_panel()
        manual_panel = QManual()
        tabs.addTab(manga_panel, "&manga")
        tabs.addTab(autodl_panel, "&autodl")
        tabs.addTab(manual_panel, "ma&nual")
        self.setCentralWidget(tabs)

    def autodl_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()

        # constructing the form
        param_line = QHBoxLayout()
        param_line.addLayout(QFolderSelect("Save location:"))
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
