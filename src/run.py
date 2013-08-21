#! /usr/bin/env python3
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This is the entry point for the nelia1 application. It creates a Qt GUI
# application, initializes the MainWindow (mainwindow.py), which in turn
# initilizes all other widgets. Then it starts a periodic timer to make python
# signal handling work in the Qt loop and runs the Qt main loop.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from datacore import *
from datacore import _dcdump
from common import *

from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    app = QApplication(sys.argv)

    loader = QtUiTools.QUiLoader()
    for name, fname in (
        ('project', 'forms/project2.ui'),
        ('log',     'forms/log2.ui'),
        ('roadmap', 'forms/roadmap2.ui')):
        f = QFile(fname)
        f.open(QFile.ReadOnly)
        dc.ui._(name).v = loader.load(f)
        f.close()
    loader.deleteLater()

    # create main window and set project as initial central widget
    dc.ui.main.v = QMainWindow()
    dc.ui.main.v.setWindowTitle('Nelia1')
    dc.ui.main.v.setWindowIcon(QIcon('img/nelia-icon32.png'))
    dc.ui.main.v.setGeometry(100,100,800,600)
    dc.ui.main.v.setCentralWidget(dc.ui.project.v)

    # load configuration
    dcloadconfig()

    # load child widget control classes
    NxProject()
    NxLog()
    NxRoadmap()

    # initialize global shortcuts
    for keys, target in [('Ctrl+w', dc.ui.main.v.close),
                         ('Ctrl+m', logMarker),
                         ('Ctrl+d', _dcdump)]:
        shortcut = QShortcut(QKeySequence(keys), dc.ui.main.v)
        shortcut.activated.connect(target)

    # show widget and give back control to run to initialize main loop
    dc.ui.main.v.show()

    # this interrupt is required to make system signal handling working. see
    # MainWindow.onSigTerm
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    sys.exit(app.exec_())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

