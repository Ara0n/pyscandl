import contextlib

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import *

from ..custom_elements import QFolderSelect, QStdoutText
from ..worker import Worker
from ... import Pyscandl
from ...modules.fetchers import FetcherEnum


class QManual(QWidget):
    def __init__(self,):
        super().__init__()
        self.setupUI()

    def setupUI(self):
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
        cancel.setDisabled(True)  # still need to figure out how to interrupt the DL
        buttons.addWidget(cancel)

        # building the layout
        layout.addLayout(first_line)
        layout.addLayout(second_line)
        layout.addWidget(self._manual_out)
        layout.addLayout(buttons)
        self.setLayout(layout)

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
        self.thread = QThread()
        self.worker = Worker(self._manual_download, self.sender())
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.signals.result.connect(lambda x: print(x))
        self.worker.signals.finished.connect(lambda: print("finished"))
        self.worker.signals.finished.connect(self.sender().setEnabled)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        # self.worker.signals.finished.connect(self.thread.deleteLater)
        self.thread.start()
