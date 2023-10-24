from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from mycanvas import *
from mymodel import *

class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        self.setGeometry(100,100,600,400)
        self.setWindowTitle("MyGLDrawer")
        self.canvas = MyCanvas()
        self.setCentralWidget(self.canvas)
        #create a model object and pass to canvas
        self.model = MyModel()
        self.canvas.setModel(self.model)
        #create a toolbar
        tb = self.addToolBar("File")
        fit = QAction(QIcon("fit.png"), "fit", self)
        bezier = QAction(QIcon("bezier.png"), "bezier", self)
        line = QAction(QIcon("line.png"), "line", self)
        tb.addAction(fit)
        tb.addAction(bezier)
        tb.addAction(line)
        tb.actionTriggered[QAction].connect(self.tbpressed)
    
    def tbpressed(self, a):
        if a.text() == "fit":
            self.canvas.fitWorldToViewport()
        if a.text() == "line":
            self.canvas.mode = 0
            print('mode', self.canvas.mode, sep=' ')
        if a.text() == "bezier":
            self.canvas.mode = 1
            print('mode', self.canvas.mode, sep=' ')
        