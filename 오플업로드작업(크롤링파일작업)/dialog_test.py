import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 300, 400, 300)   # x, y, w, h
        self.setWindowTitle('Status Window')

        #QButton
        self.button = QPushButton('Dialog Button', self)
        self.button.clicked.connect(self.dialog_open)
        self.button.setGeometry(10,10,200,50)

        #QDialog
        self.dialog = QDialog()

        #QLineEdit
        self.lineedit = QLineEdit(self)
        self.lineedit.textChanged.connect(self.change_text)

        #Enter
        self.lineedit.returnPressed.connect(self.press_text)
        self.lineedit.setGeometry(10, 10, 200, 30)

        #QLabel
        self.label = QLabel(self)
        self.label.setGeometry(10,50,200,30)

    def dialog_open(self):
        btnDialog = QPushButton("OK", self.dialog)
        btnDialog.move(100,100)
        btnDialog.clicked.connect(self.dlalog_close)

        self.dialog.setWindowTitle('Dialog')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(300,200)
        self.dialog.show()

    def dlalog_close(self):
        self.dialog.close()

    def change_text(self, txt):
        self.label.setText(txt)
        self.label.adjustSize()
    
    def press_text(self):
        self.label.setText(self.lineedit.text())
        self.label.adjustSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())