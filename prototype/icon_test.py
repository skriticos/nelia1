#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from pprint import pprint
import sys

app = QApplication(sys.argv)
mw = QMainWindow()
mw.setGeometry(200,200,640,480)

pb = QPushButton('Push Button', mw)
pb.setGeometry(50,50,250, 30)

a1 = QAction('◇   Open', pb)
a2 = QAction('◈   Current', pb)
a3 = QAction('◆   Closed', pb)
m1 = QMenu(pb)
m1.addAction(a1)
m1.addAction(a2)
m1.addAction(a3)
pb.setMenu(m1)

mw.show()

sys.exit(app.exec_())


