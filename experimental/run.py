#! /usr/bin/env python3

import sys
from PySide.QtGui import *

from mainwindow import MainWindow

# SETUP DATA INDEX
savdat = {}
rundat = {}

savdat['app_name'] = 'Nelia'
savdat['protocol'] = 1

rundat['modules'] = []

app = QApplication(sys.argv) 

# SETUP GUI
mw = MainWindow(savdat, rundat)
mw.show()

# MAIN LOOP
sys.exit(app.exec_())

# vim: set ts=4 sw=4 ai si expandtab:

