#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
import sys

app = QApplication(sys.argv)
mw = QMainWindow()

menuTop = QMenu('TopMenu')
menuV1 = QMenu('v0.x   f:0/3   i:2/7')
v1act1 = QAction('v0.1    f:0/1   i:0/0', mw)
v1act2 = QAction('v0.2    f:1/1   i:0/2', mw)
v1act3 = QAction('v0.3    f:1/1   i:1/2', mw)
v1act4 = QAction('v0.4    f:0/0   i:1/3', mw)
menuV1.addAction(v1act1)
menuV1.addAction(v1act2)
menuV1.addAction(v1act3)
menuV1.addAction(v1act4)
menuTop.addMenu(menuV1)
menuV2 = QMenu('v1.x   f:0/3   i:2/7')
v2act1 = QAction('v1.1    f:0/1   i:0/0', mw)
v2act2 = QAction('v1.2    f:1/1   i:0/2', mw)
v2act3 = QAction('v1.3    f:1/1   i:1/2', mw)
v2act4 = QAction('v1.4    f:0/0   i:1/3', mw)
menuV2.addAction(v2act1)
menuV2.addAction(v2act2)
menuV2.addAction(v2act3)
menuV2.addAction(v2act4)
menuTop.addMenu(menuV2)

push = QPushButton('PushMenu', mw)
push.setMenu(menuTop)

mw.show()
sys.exit(app.exec_())

