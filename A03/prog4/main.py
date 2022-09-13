import sys
from PyQt5.QtWidgets import *

class MyWidget (QWidget):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.setGeometry(100,100,200,150)
        self.setWindowTitle("Exercicio 1 - Somar")
        self.r1 = QLabel("a =")
        self.r2 = QLabel("b =")
        self.r3 = QLabel("a + b =")
        self.t1 = QLineEdit()
        self.t2 = QLineEdit()
        self.t3 = QLineEdit()
        self.b1 = QPushButton("Calcula")
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.r1)
        self.vbox.addWidget(self.t1)
        self.vbox.addWidget(self.r2)
        self.vbox.addWidget(self.t2)
        self.vbox.addWidget(self.b1)
        self.vbox.addWidget(self.r3)
        self.vbox.addWidget(self.t3)
        self.setLayout(self.vbox)
        #conectando sinal
        self.b1.clicked.connect(self.magic)

    #   @slot()
    def magic(self):
        a = int(self.t1.text())
        b = int(self.t2.text())
        self.t3.setText(str(a+b))





if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())