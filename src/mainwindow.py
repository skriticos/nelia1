# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import signal, os, time, PySide
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datacore import *
from datacore import _dcdump
from datastore import data
from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class MainWindow():
    def __init__(self, argv, app):
        # load ui to dc.w_*
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
            ('roadmap_diag_finalize', 'forms/roadmap_finalize_milestone.ui')):
            f = QFile(fname)
            f.open(QFile.ReadOnly)
            obj = dc.ui._(name).v= loader.load(f)
            f.close()
            if name.find('diag') > 0:
                obj.setParent(dc.ui.main.v)
                obj.setWindowFlags(Qt.Dialog)
        loader.deleteLater()
        # position module widgets
        for cname, pname in (('project', 'tab_project'),
                             ('log',     'tab_log'),
                             ('roadmap', 'tab_roadmap')):
            grid = QGridLayout()
            grid.addWidget(dc.ui._(cname).v, 0, 0)
            grid.setContentsMargins(0, 0, 0, 0)
            dc.ui.main.v.__dict__[pname].setLayout(grid)
        # icon and window size
        dc.ui.main.v.setWindowIcon(QIcon('img/nelia-icon32.png'))
        dc.ui.main.v.setGeometry(100,70,1000,600)
        # initialize modules
        dc.m.main.v    = self
        dc.m.project.v = NxProject()
        dc.m.log.v     = NxLog()
        dc.m.roadmap.v = NxRoadmap()
        # dissable all tabs except the project tab
        # they show the data from the selected project, and are in undefined
        # before a selection is made
        self.dissableTabs()
        # connect signals and slots
        dc.ui.main.v.tabnavi.currentChanged.connect(self.tabChanged)
        # global shortcuts
        for keys, target in [('Ctrl+w', dc.ui.main.v.close),
                             ('Ctrl+PgUp', self.onTabForward),
                             ('Ctrl+PgDown', self.onTabBackward),
                             ('Ctrl+s', self.onSaveShortcutActivated)]:
            shortcut = QShortcut(QKeySequence(keys), dc.ui.main.v)
            shortcut.activated.connect(target)
        # intercept close event (see self.onAboutToQuit)
        app.aboutToQuit.connect(self.onAboutToQuit)
        signal.signal(signal.SIGTERM, self.onSigTerm)
        # load configuration, if existent
        dcloadconfig()
        if dc.x.config.loaded.v:
            dc.m.project.v.loadLayout()
            dc.m.log.v.loadLayout()
            dc.m.roadmap.v.loadLayout()
        # show window
        dc.ui.main.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSaveShortcutActivated(self):
        if data.run['changed']:
            dc.m.project.v.onSaveClicked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSigTerm(self, num, frame):
        """
        We want to shut down normally on SIGTERM too. This can happen when the
        computer is turned off, without closing the application first. This
        will issue the application to quit, which in turn triggers
        onAboutToQuit. The QTimer in run.py is required for this to work.
        """
        QApplication.quit()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAboutToQuit(self):
        """
        Capture main window close event.  This might be caused by the user
        clicking the (x) window button or by exiting via the Ctrl-w shortcut
        (or any other way that tells the main window to close). Might also come
        from a SIGTERM (see onSigTerm)
        """
        dc.m.project.v.saveLayout()
        dc.m.log.v.saveLayout()
        dc.m.roadmap.v.saveLayout()
        dcsaveconfig()
        if data.run['changed']:
            if data.run['path']:
                data.save_document(data.run['path'])
            else:
                base = data.default_path
                path = os.path.join(
                    base,'.'+str(int(time.time()))+'.tmp.nelia1')
                data.save_document(path)
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
        # enable tab log and roadmap
        for i in range(1, dc.ui.main.v.tabnavi.count()):
            dc.ui.main.v.tabnavi.setTabEnabled(i, True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def dissableTabs(self):
        # disable tab log and roadmap
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

