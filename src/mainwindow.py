# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import signal
import os
import time

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from datacore import *
from common import *

from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MainWindow(QWidget):

    # Initialize main window. Load child widgets and stuff them into the
    # datacore. Initialize the GUI. Call child widget controls (project, log,
    # roadmap). Connect global callbacks (keyboard shortcuts).

    @logger('MainWindow.__init__(self)', 'self')
    def __init__(self):

        super(MainWindow, self).__init__()

        dc.m.mainwindow.v = self

        # load ui

        """
        dc.m.main.v    = self
        dc.m.log.v     = NxLog()
        dc.m.roadmap.v = NxRoadmap()
        self.dissableTabs()
        dc.ui.main.v.tabnavi.currentChanged.connect(self.tabChanged)
        for keys, target in [('Ctrl+w', dc.ui.main.v.close),
                             ('Ctrl+PgUp', self.onTabForward),
                             ('Ctrl+PgDown', self.onTabBackward),
                             ('Ctrl+s', self.onSaveShortcutActivated),
                             ('Ctrl+m', self.onAddLogMarker)]:
            shortcut = QShortcut(QKeySequence(keys), dc.ui.main.v)
            shortcut.activated.connect(target)
        app.aboutToQuit.connect(self.onAboutToQuit)
        signal.signal(signal.SIGTERM, self.onSigTerm)
        dc.ui.main.v.show()
        """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.onSaveShortcutActivated(self)', 'self')
    def onSaveShortcutActivated(self):
        if dc.r.changed.v:
            dc.m.project.v.onSaveClicked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.onSigTerm(self, num, frame)', 'self', 'num', 'frame')
    def onSigTerm(self, num, frame):
        QApplication.quit()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.onAboutToQuit(self)', 'self')
    def onAboutToQuit(self):
        dc.m.project.v.saveLayout()
        dc.m.log.v.saveLayout()
        dc.m.roadmap.v.saveLayout()
        if dc.r.changed.v:
            if not dc.x.path.v:
                dc.x.path.v = os.path.join(dc.x.default.path.v,
                       '.{}.tmp.nelia1'.format(str(int(time.time()))))
            dcsave()
        dcsaveconfig()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.onTabForward(self)', 'self')
    def onTabForward(self):
        tab_index = dc.ui.main.v.tabnavi.currentIndex()
        tab_count = dc.ui.main.v.tabnavi.count()
        if tab_index+1 == tab_count:
            dc.ui.main.v.tabnavi.setCurrentIndex(0)
        elif dc.ui.main.v.tabnavi.isTabEnabled(tab_index+1):
            dc.ui.main.v.tabnavi.setCurrentIndex(tab_index+1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.onTabBackward(self)', 'self')
    def onTabBackward(self):
        tab_index = dc.ui.main.v.tabnavi.currentIndex()
        tab_count = dc.ui.main.v.tabnavi.count()
        if tab_index == 0:
            if dc.ui.main.v.tabnavi.isTabEnabled(tab_count-1):
                dc.ui.main.v.tabnavi.setCurrentIndex(tab_count-1)
        else:
            dc.ui.main.v.tabnavi.setCurrentIndex(tab_index-1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.enableTabs(self)', 'self')
    def enableTabs(self):
        for i in range(1, dc.ui.main.v.tabnavi.count()):
            dc.ui.main.v.tabnavi.setTabEnabled(i, True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.dissableTabs(self)', 'self')
    def dissableTabs(self):
        for i in range(1, dc.ui.main.v.tabnavi.count()):
            dc.ui.main.v.tabnavi.setTabEnabled(i, False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('MainWindow.tabChanged(self)', 'self', 'target')
    def tabChanged(self, target):
        tab_widget = dc.ui.main.v.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())
        if cur_tab_name == '&Log':
            dc.m.log.v.onShowTab()
        if cur_tab_name == '&Roadmap':
            dc.m.roadmap.v.onShowTab()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

