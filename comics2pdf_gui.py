#!/usr/bin/env python3

import os
import sys
import shutil
import tempfile
import platform

import zipfile
import patoolib
from PyQt5 import QtCore, QtWidgets
from PIL import Image


class Explorer(QtWidgets.QWidget):

    def __init__(self, isFile):
        super().__init__()
        self.title = "Explorer"
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.path = ""
        self.isFile = isFile
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        if self.isFile:
            self.openFileNameDialog()
        else:
            self.openDirectoryNameDialog()

        self.show()
        self.hide()

    def openFileNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Find File", "", "CBR and CBZ files (*.cbr, *.cbz)", options=options
        )
        if fileName:
            self.path = fileName

    def openDirectoryNameDialog(self):
        options = QtWidgets.QFileDialog.Options()
        fileName = QtWidgets.QFileDialog.getExistingDirectory(self, options=options)
        if fileName:
            self.path = fileName


class AppGUI(object):

    def __init__(self):
        super().__init__()
        self.path = os.getcwd()
        self.progress = 0
        self.global_process = 0
        self.nb_files = 0
        self.done = 0
        self.tmp_directory = tempfile.gettempdir()
        self.current_os = platform.system()

    def separator(self):
        if self.current_os == "Windows":
            return "\\"
        else:
            return "/"

    def on_button_clicked(self):
        explorer = Explorer(self.file.isChecked())
        if explorer.path:
            self.path = explorer.path
        self.pathTo.setText(self.path)

    def setupUi(self, Form):
        Form.setObjectName("Comics2pdf GUI")
        Form.setFixedSize(536, 164)
        self.error_dialog = QtWidgets.QErrorMessage()

        self.convert = QtWidgets.QPushButton(Form)
        self.convert.setGeometry(QtCore.QRect(420, 110, 91, 33))
        self.convert.setObjectName("convert")
        self.convert.clicked.connect(self.start_convert)

        self.conversionProgress = QtWidgets.QProgressBar(Form)
        self.conversionProgress.setGeometry(QtCore.QRect(20, 110, 381, 23))
        self.conversionProgress.setProperty("value", self.progress)
        self.conversionProgress.setObjectName("conversionProgress")

        self.pathTo = QtWidgets.QLineEdit(Form)
        self.pathTo.setGeometry(QtCore.QRect(20, 20, 371, 31))
        self.pathTo.setObjectName("pathTo")

        self.browse = QtWidgets.QPushButton(Form)
        self.browse.setGeometry(QtCore.QRect(420, 20, 91, 33))
        self.browse.setObjectName("browse")
        self.browse.clicked.connect(self.on_button_clicked)

        self.inputType = QtWidgets.QButtonGroup(Form)
        self.inputType.setObjectName("inputType")
        self.folder = QtWidgets.QRadioButton(Form)
        self.folder.setObjectName("folder")
        self.folder.setChecked(True)
        self.folder.setGeometry(QtCore.QRect(30, 70, 81, 20))
        self.file = QtWidgets.QRadioButton(Form)
        self.file.setObjectName("file")
        self.file.setChecked(False)
        self.file.setGeometry(QtCore.QRect(120, 70, 81, 20))
        self.inputType.addButton(self.folder)
        self.inputType.addButton(self.file)

        self.indication = QtWidgets.QLabel(Form)
        self.indication.setEnabled(False)
        self.indication.setGeometry(QtCore.QRect(240, 70, 171, 17))
        self.indication.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.indication.setObjectName("indication")

        self.ratio = QtWidgets.QLabel(Form)
        self.ratio.setEnabled(False)
        self.ratio.setGeometry(QtCore.QRect(455, 70, 171, 17))
        self.ratio.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.ratio.setObjectName("ratio")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Comics2pdf GUI"))
        self.folder.setText(_translate("Form", "Folder"))
        self.convert.setText(_translate("Form", "Convert"))
        self.browse.setText(_translate("Form", "Browse"))
        self.file.setText(_translate("Form", "File"))
        self.pathTo.setText(_translate("Form", self.path))

    def start_convert(self):
        self.indication.setEnabled(True)
        self.ratio.setEnabled(True)
        if self.folder.isChecked() and os.path.isdir(self.pathTo.text()):
            self.opendir(self.pathTo.text())
        elif self.file.isChecked() and os.path.isfile(self.pathTo.text()):
            self.nb_files += 1
            self.launch_convert(self.pathTo.text())
        else:
            return
        self.conversionProgress.setProperty("value", 0)
        self.nb_files = 0
        self.global_process = 0
        self.done = 0
        self.indication.setText("")
        self.ratio.setText("")

    def opendir(self, directory):
        directory_list = sorted(os.listdir(directory))
        for file in directory_list:
            if file.endswith(".cbz") or file.endswith(".CBZ") or file.endswith(".cbr") or file.endswith(".CBR"):
                self.nb_files += 1
        for file in directory_list:
            self.launch_convert(directory + "/" + file)

    def launch_convert(self, file):
        if file[-4:] == ".cbz" or file[-4:] == ".zip":
            self.handle_zip(file)
        elif file[-4:] == ".cbr" or file[-4:] == ".rar":
            self.handle_rar(file)

    def handle_rar(self, filein):
        tmp_dir = self.tmp_directory + self.separator() + "c2p" + self.separator()
        try:
            os.mkdir(tmp_dir)
        except:
            print("Temporary folder already exists")
        patoolib.extract_archive(filein, outdir=tmp_dir)
        newfile = filein.replace(filein[-4:], ".pdf")
        self.to_pdf(newfile, tmp_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def handle_zip(self, filein):
        tmp_dir = self.tmp_directory + self.separator() + "c2p" + self.separator()
        zip_ref = zipfile.ZipFile(filein, "r")
        zip_ref.extractall(tmp_dir)
        zip_ref.close()
        newfile = filein.replace(filein[-4:], ".pdf")
        self.to_pdf(newfile, tmp_dir)
        shutil.rmtree(tmp_dir, ignore_errors=True)

    def get_files(self, f, dir):
        files = os.listdir(dir)
        for file in files:
            path = dir + self.separator() + file
            if os.path.isdir(path):
                self.get_files(f, path)
            else:
                f.append(path)

    def to_pdf(self, filename, newdir):
        self.indication.setText("Exctracting images...")
        self.ratio.setText(str(self.done) + self.separator() + str(self.nb_files))

        image_list = []
        self.get_files(image_list, newdir)

        im_list = list()
        is_first_image = True
        im = None
        increased = False
        index = 0
        list_len = len(image_list)

        for image in sorted(image_list):
            index += 1
            local_process = index / list_len * 100 // self.nb_files
            self.conversionProgress.setProperty("value", "{0:.0f}".format(local_process + self.global_process))

            if local_process * self.nb_files > 95:
                if increased == False:
                    self.done += 1
                    increased = True
                self.indication.setText("Saving the created file...")
                self.ratio.setText(str(self.done) + "/" + str(self.nb_files))
            img = Image.open(image)

            try:
                if img.mode == "RGBA":
                    img = img.convert("RGB")
                img.save(image, dpi=(96, 96))
            except:
                print("Error")

            if is_first_image:
                im = img
                is_first_image = False
            else:
                im_list.append(img)

        im.save(filename, "PDF", resolution=100.0, save_all=True, append_images=im_list)
        shutil.rmtree(newdir, ignore_errors=True)
        self.global_process += local_process


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = AppGUI()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
