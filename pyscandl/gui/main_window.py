import contextlib

from PyQt5.QtCore import QThreadPool, Qt, pyqtSignal
from PyQt5.QtWidgets import *

from .custom_elements import QFolderSelect, QStdoutText
from .panels.manga import QManga
from .worker import Worker
from .. import Pyscandl
from ..modules.autodl import Controller
from ..modules.fetchers import FetcherEnum


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
        manual_panel = self.manual_panel()
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

    def manual_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        top_layout = QGridLayout()

        # constructing 2 line form in the QGridLayout
        ## first line: save location, quiet, tiny, download mode
        first_line = QHBoxLayout()
        first_line.addLayout(QFolderSelect("Save location:"))
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
