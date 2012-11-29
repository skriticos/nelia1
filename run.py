#! /usr/bin/env python3

import sys
from PySide.QtGui import *
from mainwindow import MainWindow

app = QApplication(sys.argv) 

# SETUP GUI
mw = MainWindow()
mw.widget.show()

# MAIN LOOP
sys.exit(app.exec_())

# vim: set ts=4 sw=4 ai si expandtab:

