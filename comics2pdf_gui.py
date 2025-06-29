#!/usr/bin/env python3

import os
import sys
from pathlib import Path
from typing import Optional

from PyQt5 import QtCore, QtWidgets
from comics2pdf import ComicConverter


class Explorer(QtWidgets.QWidget):

    def __init__(self, isFile: bool) -> None:
        super().__init__()
        self.title = "Explorer"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.path = ""
        self.isFile = isFile
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        if self.isFile:
            self.openFileNameDialog()
        else:
            self.openDirectoryNameDialog()

        self.show()
        self.hide()

    def openFileNameDialog(self) -> None:
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Find File", "", "CBR and CBZ files (*.cbr, *.cbz)", options=options
        )
        if fileName:
            self.path = fileName

    def openDirectoryNameDialog(self) -> None:
        options = QtWidgets.QFileDialog.Options()
        fileName = QtWidgets.QFileDialog.getExistingDirectory(self, options=options)
        if fileName:
            self.path = fileName


class AppGUI(object):

    def __init__(self) -> None:
        super().__init__()
        self.path: str = os.getcwd()
        self.output_path: str = ""
        self.progress: int = 0
        self.converter: Optional[ComicConverter] = None

    def on_button_clicked(self) -> None:
        explorer = Explorer(self.file.isChecked())
        if explorer.path:
            self.path = explorer.path
        self.pathTo.setText(self.path)

    def on_output_button_clicked(self) -> None:
        options = QtWidgets.QFileDialog.Options()
        output_dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if output_dir:
            self.output_path = output_dir
            self.outputPathTo.setText(self.output_path)

    def setupUi(self, Form: QtWidgets.QWidget) -> None:
        Form.setObjectName("Comics2pdf GUI")
        Form.setFixedSize(536, 220)  # Increased height for new controls
        self.error_dialog = QtWidgets.QErrorMessage()

        # Input path controls
        self.pathTo = QtWidgets.QLineEdit(Form)
        self.pathTo.setGeometry(QtCore.QRect(20, 20, 371, 31))
        self.pathTo.setObjectName("pathTo")

        self.browse = QtWidgets.QPushButton(Form)
        self.browse.setGeometry(QtCore.QRect(420, 20, 91, 33))
        self.browse.setObjectName("browse")
        self.browse.clicked.connect(self.on_button_clicked)

        # Output path controls
        self.outputPathLabel = QtWidgets.QLabel(Form)
        self.outputPathLabel.setGeometry(QtCore.QRect(20, 60, 100, 17))
        self.outputPathLabel.setText("Output Directory:")

        self.outputPathTo = QtWidgets.QLineEdit(Form)
        self.outputPathTo.setGeometry(QtCore.QRect(20, 80, 371, 31))
        self.outputPathTo.setObjectName("outputPathTo")
        self.outputPathTo.setPlaceholderText("Leave empty to use same directory as input")

        self.browseOutput = QtWidgets.QPushButton(Form)
        self.browseOutput.setGeometry(QtCore.QRect(420, 80, 91, 33))
        self.browseOutput.setObjectName("browseOutput")
        self.browseOutput.setText("Browse")
        self.browseOutput.clicked.connect(self.on_output_button_clicked)

        # Input type radio buttons
        self.inputType = QtWidgets.QButtonGroup(Form)
        self.inputType.setObjectName("inputType")
        self.folder = QtWidgets.QRadioButton(Form)
        self.folder.setObjectName("folder")
        self.folder.setChecked(True)
        self.folder.setGeometry(QtCore.QRect(30, 120, 81, 20))
        self.file = QtWidgets.QRadioButton(Form)
        self.file.setObjectName("file")
        self.file.setChecked(False)
        self.file.setGeometry(QtCore.QRect(120, 120, 81, 20))
        self.inputType.addButton(self.folder)
        self.inputType.addButton(self.file)

        # Processing mode controls
        self.processingMode = QtWidgets.QButtonGroup(Form)
        self.processingMode.setObjectName("processingMode")
        self.asyncMode = QtWidgets.QRadioButton(Form)
        self.asyncMode.setObjectName("asyncMode")
        self.asyncMode.setChecked(True)
        self.asyncMode.setGeometry(QtCore.QRect(250, 120, 81, 20))
        self.asyncMode.setText("Async")
        self.syncMode = QtWidgets.QRadioButton(Form)
        self.syncMode.setObjectName("syncMode")
        self.syncMode.setChecked(False)
        self.syncMode.setGeometry(QtCore.QRect(340, 120, 81, 20))
        self.syncMode.setText("Sync")
        self.processingMode.addButton(self.asyncMode)
        self.processingMode.addButton(self.syncMode)

        # Progress and status controls
        self.conversionProgress = QtWidgets.QProgressBar(Form)
        self.conversionProgress.setGeometry(QtCore.QRect(20, 150, 381, 23))
        self.conversionProgress.setProperty("value", self.progress)
        self.conversionProgress.setObjectName("conversionProgress")

        self.convert = QtWidgets.QPushButton(Form)
        self.convert.setGeometry(QtCore.QRect(420, 150, 91, 33))
        self.convert.setObjectName("convert")
        self.convert.clicked.connect(self.start_convert)

        self.indication = QtWidgets.QLabel(Form)
        self.indication.setEnabled(False)
        self.indication.setGeometry(QtCore.QRect(20, 180, 250, 17))
        self.indication.setObjectName("indication")

        self.ratio = QtWidgets.QLabel(Form)
        self.ratio.setEnabled(False)
        self.ratio.setGeometry(QtCore.QRect(280, 180, 100, 17))
        self.ratio.setObjectName("ratio")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form: QtWidgets.QWidget) -> None:
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Comics2pdf GUI"))
        self.folder.setText(_translate("Form", "Folder"))
        self.convert.setText(_translate("Form", "Convert"))
        self.browse.setText(_translate("Form", "Browse"))
        self.file.setText(_translate("Form", "File"))
        self.pathTo.setText(_translate("Form", self.path))

    def progress_update(self, total_files: int, completed_files: int, current_file: str) -> None:
        """Callback for progress updates from ComicConverter."""
        if total_files > 0:
            progress_percent = int((completed_files / total_files) * 100)
            self.conversionProgress.setProperty("value", progress_percent)

        self.indication.setText(f"Processing: {current_file}")
        self.ratio.setText(f"{completed_files}/{total_files}")

        # Force GUI update
        QtWidgets.QApplication.processEvents()

    def start_convert(self) -> None:
        # Create converter with current settings and progress callback
        output_dir = Path(self.outputPathTo.text()) if self.outputPathTo.text().strip() else None
        use_async = self.asyncMode.isChecked() and self.folder.isChecked()

        self.converter = ComicConverter(
            verbose=False, output_dir=output_dir, use_async=use_async, progress_callback=self.progress_update
        )

        self.indication.setEnabled(True)
        self.ratio.setEnabled(True)
        self.conversionProgress.setProperty("value", 0)

        try:
            if self.folder.isChecked() and os.path.isdir(self.pathTo.text()):
                self.converter.process_directory(Path(self.pathTo.text()))
            elif self.file.isChecked() and os.path.isfile(self.pathTo.text()):
                self.converter.process_single_file(Path(self.pathTo.text()))
            else:
                self.indication.setText("Invalid path or file not found")
                return

            # Conversion completed
            self.conversionProgress.setProperty("value", 100)
            self.indication.setText("Conversion completed!")

        except Exception as e:
            self.indication.setText(f"Error: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AppGUI()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
