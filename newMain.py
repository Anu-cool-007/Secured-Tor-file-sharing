import os
import sys

from PyQt5 import QtWidgets, uic

from Ui_DesignWindow import Ui_MainWindow
from serve_ui import Ui_Form
import encrypt
import decrypt
from torshare import TorShare


class ServeFile(QtWidgets.QWidget, Ui_MainWindow):
    def __init__(self, url, torsh):
        super().__init__()
        self.setupUi(self)
        self.torsh = torsh

        self.lineEdit.setText(url)
        self.stop_btn.clicked.connect(self.stop_serving)

    def stop_serving(self):
        print(" * Shutting down the hidden service")
        self.torsh.app_process.terminate()
        self.torsh.app_process.join()
        self.torsh.stop_service()
        self.close()


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.torsh = TorShare()

        self.browseBtn.clicked.connect(self.get_filepath)
        self.encryptBtn.clicked.connect(self.encrypt_file)
        self.serveBtn.clicked.connect(self.tor_share)

        self.browseBtn_2.clicked.connect(self.get_filepath)
        self.encryptBtn_2.clicked.connect(self.decrypt_file)

        self.show()

    def get_filepath(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, 'File', os.getenv('HOME'))
        print(filename)
        if self.Tabs.currentIndex() == 0:
            self.lineEdit.setText(filename[0])
        elif self.Tabs.currentIndex() == 1:
            self.lineEdit_2.setText(filename[0])

    def encrypt_file(self):
        pub_key = self.pub_key.toPlainText().encode()
        result = encrypt.encrypt(pub_key, self.lineEdit.text())
        QtWidgets.QMessageBox.information(self, "Result", result)

    def decrypt_file(self):
        priv_key = self.pub_key_2.toPlainText().encode()
        result = decrypt.decrypt(priv_key, self.lineEdit_2.text())
        QtWidgets.QMessageBox.information(self, "Result", result)

    def tor_share(self):
        self.torsh.connect()
        if not self.torsh.is_connected():
            QtWidgets.QMessageBox.warning(self, "Error", "Could not connect")
            return

        self.torsh.authenticate()
        if not self.torsh.controller.is_authenticated():
            QtWidgets.QMessageBox.warning(
                self, "Error", "Could not authenticate")
            return
        file = self.filepath_ledit.text()
        if not file.endswith(".enc"):
            file += ".enc"

        if not os.path.isfile(file):
            QtWidgets.QMessageBox.warning(self, "Error", "File does not exist")
            return

        self.torsh.create_service(file)

        self.serve_widget = ServeFile(self.torsh.hostname, self.torsh)
        self.serve_widget.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
