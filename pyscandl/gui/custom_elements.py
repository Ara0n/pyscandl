from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QFileIconProvider, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, \
    QTextEdit


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


class QErrorPopup(QMessageBox):
    def __init__(self, icon=QMessageBox.Critical, title="error", text=None, info_text=None, detailed_text=None):
        super().__init__()
        self.setupUI(icon, title, text, info_text, detailed_text)
        self.exec()

    def setupUI(self, icon, title, text, info_text, detailed_text):
        self.setIcon(icon)
        self.setWindowTitle(title)
        if text:
            self.setText(text)
        if info_text:
            self.setInformativeText(info_text)
        if detailed_text:
            self.setDetailedText(detailed_text)

class QFolderSelect(QHBoxLayout):
    def __init__(self, label="Save location:"):
        super().__init__()
        self.setupUI(label)

    def setupUI(self, label):
        if label:
            self.addWidget(QLabel(label))
        self.path = QLineEdit()
        file_button = QPushButton(QFileIconProvider().icon(QFileIconProvider.Folder), "")
        file_button.clicked.connect(self._folder_select)
        self.addWidget(self.path)
        self.addWidget(file_button)

    def _folder_select(self):
        sender = self.sender()
        folder_select = QFileDialog()
        folder_select.setFileMode(QFileDialog.DirectoryOnly)
        folder_select.fileSelected.connect(sender.parent().findChild(QLineEdit).setText)
        if self.path.text():
            folder_select.setDirectory(self.path.text())
        folder_select.exec()
