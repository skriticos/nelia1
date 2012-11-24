#! /usr/bin/env python3

import sys
from PySide import QtGui

class Example(QtGui.QMainWindow):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):               
        
        exitAction = QtGui.QAction(QtGui.QIcon('open.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        pb = QtGui.QPushButton('Push Button', self)
        pb.setGeometry(50,50,250, 30)
        m1 = QtGui.QMenu(pb)
        m1.addAction(exitAction)
        pb.setMenu(m1)
        
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Menubar')    
        self.show()
        
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
