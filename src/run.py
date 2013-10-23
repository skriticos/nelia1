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
from common2 import *

from project import NxProject, NxDocument
from log     import NxLog
from roadmap import NxRoadmap

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':

    dc.auto.v = True
    dc.x.app.v = app = QApplication(sys.argv)
    dcloadconfig()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # init gui
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    loader = QtUiTools.QUiLoader()
    for name, fname in (
        ('project', 'forms/project2.ui'),
        ('log',     'forms/log2.ui'),
        ('roadmap', 'forms/roadmap2.ui'),
        ('finalize','forms/finalize2.ui')):
        f = QFile(fname)
        f.open(QFile.ReadOnly)
        dc.ui._(name).v = loader.load(f)
        f.close()
    loader.deleteLater()

    dc.ui.main.v = QMainWindow()
    dc.ui.main.v.setWindowTitle('Nelia1')
    dc.ui.main.v.setWindowIcon(QIcon('img/nelia-icon32.png'))
    dc.ui.main.v.setGeometry(100,100,800,600)
    dc.ui.main.v.setCentralWidget(dc.ui.project.v)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # init modules
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    NxDocument()
    NxProject()
    NxLog()
    NxRoadmap()

    dc.m.project.v.initNavi()
    dc.m.log.v.initNavi()
    dc.m.roadmap.v.initNavi()

    project_list_header_widths          = [ 50, 200, 100, 150, 100, 100, 100, 150, 150 ]
    log_list_header_widths              = [ 50, 300, 100, 150, 150 ]
    milestone_item_list_header_widths   = [ 50, 300, 100, 100, 100, 100, 150, 150 ]

    def applyHeaderWidths(widget, widths):
        for i, v in enumerate(widths):
            widget.setColumnWidth(i, v)


    if not dc.x.config.loaded.v:

        applyHeaderWidths(dc.ui.project.v.tbl_project_list,
                          project_list_header_widths)
        applyHeaderWidths(dc.ui.log.v.tbl_log_list,
                          log_list_header_widths)
        applyHeaderWidths(dc.ui.roadmap.v.tbl_mi_list,
                          milestone_item_list_header_widths)

        dc.x.project.horizontal_header.v.setSortIndicator(
            7, Qt.SortOrder.DescendingOrder)
        dc.x.log.horizontal_header.v.setSortIndicator(
            0, Qt.SortOrder.DescendingOrder)
        dc.x.roadmap.horizontal_header.v.setSortIndicator(
            6, Qt.SortOrder.DescendingOrder)

        saveLayout('project')
        saveLayout('log')
        saveLayout('roadmap')

    dc.m.project.projectlist.v.initProjectFilterControls()
    dc.m.log.loglist.v.initLogFilterControls()
    dc.m.roadmap.milist.v.initRoadmapFilterControls()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # init global shortcuts
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    for keys, target in [('Ctrl+w', dc.ui.main.v.close),
                         ('Ctrl+m', logMarker),
                         ('Ctrl+d', _dcdump)]:
        shortcut = QShortcut(QKeySequence(keys), dc.ui.main.v)
        shortcut.activated.connect(target)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # enter main loop
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    dc.ui.main.v.show()

    if len(sys.argv) > 1:
        pa = []
        for s in sys.argv[1:]:
            if s.endswith('\\'):
                s = s[:-1]
            pa.append(s)
        p = ' '.join(pa)
        p = os.path.expanduser(p)
        print(p)
        if os.path.exists(p):

            dcload(p)
            dc.spid.v = dc.s.spid.v
            dc.sp = dc.s._(dc.spid.v)
            dc.states.project.changed.v = False
            dc.states.project.focustable.v = True
            dc.states.project.newload.v = True
            dc.m.project.projectlist.v.reloadTable()

    # this interrupt is required to make system signal handling working
    timer = QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    dc.auto.v = False

    sys.exit(app.exec_())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

