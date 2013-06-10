# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import signal, os, time, PySide
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datacore import *
from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MainWindow():
    def __init__(self, argv, app):
        loader = QtUiTools.QUiLoader()
        for name, fname in (
            ('main',                  'forms/mainwindow.ui'),
            ('project',               'forms/project.ui'),
            ('project_diag_help',     'forms/project_help.ui'),
            ('log',                   'forms/log.ui'),
            ('roadmap',               'forms/roadmap.ui'),
            ('project_diag_new',      'forms/project_diag_new.ui'),
            ('project_diag_edit',     'forms/project_diag_edit.ui'),
            ('log_diag_new',          'forms/log_new_entry.ui'),
            ('roadmap_diag_add',      'forms/roadmap_add.ui'),
            ('roadmap_diag_edit',     'forms/roadmap_edit.ui'),
            ('roadmap_diag_finalize', 'forms/roadmap_finalize_milestone.ui')):
            f = QFile(fname)
            f.open(QFile.ReadOnly)
            obj = dc.ui._(name).v= loader.load(f)
            f.close()
            if name.find('diag') > 0:
                obj.setParent(dc.ui.main.v)
                obj.setWindowFlags(Qt.Dialog)
        loader.deleteLater()
        for cname, pname in (('project', 'tab_project'),
                             ('log',     'tab_log'),
                             ('roadmap', 'tab_roadmap')):
            grid = QGridLayout()
            grid.addWidget(dc.ui._(cname).v, 0, 0)
            grid.setContentsMargins(0, 0, 0, 0)
            dc.ui.main.v.__dict__[pname].setLayout(grid)
        dc.ui.main.v.setWindowIcon(QIcon('img/nelia-icon32.png'))
        dc.ui.main.v.setGeometry(100,70,1000,600)
        dcloadconfig()
        dc.m.main.v    = self
        dc.m.project.v = NxProject()
        dc.m.log.v     = NxLog()
        dc.m.roadmap.v = NxRoadmap()
        self.dissableTabs()
        dc.ui.main.v.tabnavi.currentChanged.connect(self.tabChanged)
        for keys, target in [('Ctrl+w', dc.ui.main.v.close),
                             ('Ctrl+PgUp', self.onTabForward),
                             ('Ctrl+PgDown', self.onTabBackward),
                             ('Ctrl+s', self.onSaveShortcutActivated)]:
            shortcut = QShortcut(QKeySequence(keys), dc.ui.main.v)
            shortcut.activated.connect(target)
        app.aboutToQuit.connect(self.onAboutToQuit)
        signal.signal(signal.SIGTERM, self.onSigTerm)
        if dc.x.config.loaded.v:
            dc.m.project.v.loadLayout()
            dc.m.log.v.loadLayout()
            dc.m.roadmap.v.loadLayout()
        dc.ui.main.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSaveShortcutActivated(self):
        if dc.r.changed.v:
            dc.m.project.v.onSaveClicked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSigTerm(self, num, frame):
        QApplication.quit()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAboutToQuit(self):
        dc.m.project.v.saveLayout()
        dc.m.log.v.saveLayout()
        dc.m.roadmap.v.saveLayout()
        if dc.r.changed.v:
            if not dc.r.path.v:
                dc.x.path.v = os.path.join(dc.x.default.path.v,
                       '.{}.tmp.nelia1'.format(str(int(time.time()))))
            dcsave()
        dcsaveconfig()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabForward(self):
        tab_index = dc.ui.main.v.tabnavi.currentIndex()
        tab_count = dc.ui.main.v.tabnavi.count()
        if tab_index+1 == tab_count:
            dc.ui.main.v.tabnavi.setCurrentIndex(0)
        elif dc.ui.main.v.tabnavi.isTabEnabled(tab_index+1):
            dc.ui.main.v.tabnavi.setCurrentIndex(tab_index+1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onTabBackward(self):
        tab_index = dc.ui.main.v.tabnavi.currentIndex()
        tab_count = dc.ui.main.v.tabnavi.count()
        if tab_index == 0:
            if dc.ui.main.v.tabnavi.isTabEnabled(tab_count-1):
                dc.ui.main.v.tabnavi.setCurrentIndex(tab_count-1)
        else:
            dc.ui.main.v.tabnavi.setCurrentIndex(tab_index-1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def enableTabs(self):
        for i in range(1, dc.ui.main.v.tabnavi.count()):
            dc.ui.main.v.tabnavi.setTabEnabled(i, True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dissableTabs(self):
        for i in range(1, dc.ui.main.v.tabnavi.count()):
            dc.ui.main.v.tabnavi.setTabEnabled(i, False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def tabChanged(self):
        tab_widget = dc.ui.main.v.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())
        if cur_tab_name == '&Log':
            dc.m.log.v.onShowTab()
        if cur_tab_name == '&Roadmap':
            dc.m.roadmap.v.onShowTab()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

