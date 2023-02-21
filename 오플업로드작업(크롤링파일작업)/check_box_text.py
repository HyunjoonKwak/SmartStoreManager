import sys
from PyQt5.QtWidgets import QLabel, QBoxLayout, QMainWindow, QApplication, QGroupBox, QCheckBox, \
    QButtonGroup, QLineEdit, QPushButton, QDialog
from PyQt5.QtCore import pyqtSlot, Qt


class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 500, 1000, 300)   # x, y, w, h
        self.setWindowTitle('Status Window')

        #QLabel
        self.label = QLabel(self)
        self.label.setGeometry(10,10,900,30)
        self.label.setStyleSheet('background-color : #FFFFFF')
 
         #QLineEdit
        self.lineedit = QLineEdit(self)
        self.lineedit.textChanged.connect(self.change_text)
        self.lineedit.setGeometry(10,210,900,30)

        #Enter
        self.lineedit.returnPressed.connect(self.press_text)
        self.lineedit.setGeometry(10, 210, 900, 30)

        #QCheckBox1
        self.checkBox1 = QCheckBox('Check3 Button', self)
        self.checkBox1.stateChanged.connect(self.check_select1)

        self.checkBox2 = QCheckBox('Check3 Button', self)
        self.checkBox2.stateChanged.connect(self.check_select2)

        self.boxlayout = QBoxLayout(QBoxLayout.TopToBottom, parent = self)
        self.boxlayout.addWidget(self.checkBox1)
        self.boxlayout.addWidget(self.checkBox2)

        #QGroupBox
        self.groupbox = QGroupBox('Group Box', self)
        self.groupbox.setLayout(self.boxlayout)
        self.groupbox.setGeometry(10,60,300,150)

        #QButton
        self.button = QPushButton('Check Option', self)
        self.button.clicked.connect(self.dialog_open)
        self.button.setGeometry(10, 240, 200, 50)

        self.dialog = QDialog()
        # self.buttongroup = QButtonGroup(self)
        # self.buttongroup.setExclusive(True)
        # self.buttongroup.addButton(self.checkBox1, 1)
        # self.buttongroup.addButton(self.checkBox2, 2)
        # self.buttongroup.buttonClicked.connect(self.check_buttongroup)

    def check_buttongroup(self):
        print('call button group function')
 
    def change_text(self, txt):
        self.label.setText(txt)
        self.label.adjustSize()
    
    def press_text(self):
        self.label.setText(self.lineedit.text())
        self.label.adjustSize()
    
    def check_select1(self, state):
        if state == Qt.Checked:
            self.label.setText('Checked 1')
        else:
            self.label.setText('Unchecked 1')
    def check_select2(self, state):
        if state == Qt.Checked:
            self.label.setText('Checked 2')
        else:
            self.label.setText('Unchecked 2')
    
    def dialog_open(self):
        btnDialog = QPushButton("OK", self.dialog)
        btnDialog.move(100,100)
        btnDialog.clicked.connect(self.dialog_close)

        self.dialog.setWindowTitle('Dialog')
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.resize(300,200)
        self.dialog.show()

    def dialog_close(self):
        self.dialog.close()
        print('dialog_close function')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())