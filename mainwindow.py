#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject
from log     import NxLog
from roadmap import NxRoadmap

from datastore import NxDataStore

class MainWindow(QObject):

    """
        The main window control class contains the application main
        container window and container tab widget. It commands global
        actions, like tab switching, exit handling, saving and loading.
    """

    def __init__(self, argv):

        super().__init__()

        # setup datastore
        data = self.data = NxDataStore(self)

        # Load UI
        loader = QtUiTools.QUiLoader()
        for name, fname in (('w_main',                    'forms/mainwindow.ui'),
                            ('w_project',                 'forms/project.ui'),
                            ('w_log',                     'forms/log.ui'),
                            ('w_roadmap',                 'forms/roadmap.ui'),
                            ('w_project_diag_new',        'forms/project_diag_new.ui'),
                            ('w_project_diag_edit',       'forms/project_diag_edit.ui'),
                            ('w_log_diag_detail',         'forms/log_detail.ui'),
                            ('w_log_diag_new',            'forms/log_new_entry.ui'),
                            ('w_roadmap_diag_add',        'forms/roadmap_add.ui')):
            f = QFile(fname)
            f.open(QFile.ReadOnly)
            obj = self.__dict__[name] = loader.load(f)
            f.close()
            if name.find('diag') > 0:
                obj.setParent(self.w_main)
                obj.setWindowFlags(Qt.Dialog)
            self.data.run[name] = obj
        loader.deleteLater()

        # position module widgets
        for cname, pname in (('w_project', 'tab_project'),
                             ('w_log',     'tab_log'),
                             ('w_roadmap', 'tab_roadmap')):
            grid = QGridLayout()
            grid.addWidget(self.__dict__[cname], 0, 0)
            grid.setContentsMargins(0, 0, 0, 0)
            self.w_main.__dict__[pname].setLayout(grid)

        # icon and window size
        self.w_main.setWindowIcon(QIcon('img/nelia-icon32.png'))
        self.w_main.setGeometry(100,70,1000,600)

        # initialize modules
        self.data.run['mainwindow'] = self
        self.data.run['project']    = NxProject(self, data, self.w_project)
        self.data.run['log']        = NxLog    (self, data, self.w_log)
        self.data.run['roadmap']    = NxRoadmap(self, data, self.w_roadmap)

        # Dissable all tabs except the project tab.
        # They show the data from the selected project, and are in undefined
        # before a selection is made.
        self.dissableTabs()

        # Connect signals and slots.
        self.w_main.tabnavi.currentChanged.connect(self.tabChanged)

        # Global shortcuts.
        close_shortcut = QShortcut(QKeySequence('Ctrl+w'), self.w_main)
        close_shortcut.activated.connect(self.w_main.close)
        switch_forward = QShortcut(QKeySequence('Ctrl+PgUp'), self.w_main)
        switch_forward.activated.connect(self.onTabForward)
        switch_backward = QShortcut(QKeySequence('Ctrl+PgDown'), self.w_main)
        switch_backward.activated.connect(self.onTabBackward)
        save = QShortcut(QKeySequence('Ctrl+s'), self.w_main)
        save.activated.connect(self.data.save)

        # Intercept close event (see self.eventFilter).
        QObject.installEventFilter(self.w_main, self)


    def eventFilter(self, obj, event):

        """
            Capture main window close event.
            This might be caused by the user clicking the (x) window button or by
            exiting via the Ctrl-w shortcut (or any other way that tells the main
            window to close).
        """

        if obj == self.w_main:
            if isinstance(event, QCloseEvent):
                # TODO: handle close window (e.g. show warning, offer to save)
                pass
        res = False
        try:
            res = QObject.eventFilter(self.w_main, obj, event)
        except:
            pass
        return res


    def onTabForward(self):

        # get current tab index
        tab_index = self.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = self.w_main.tabnavi.count()

        # next tab
        if tab_index+1 == tab_count:
            self.w_main.tabnavi.setCurrentIndex(0)
        elif self.w_main.tabnavi.isTabEnabled(tab_index+1):
            self.w_main.tabnavi.setCurrentIndex(tab_index+1)


    def onTabBackward(self):

        # get current tab index
        tab_index = self.w_main.tabnavi.currentIndex()

        # get max index
        tab_count = self.w_main.tabnavi.count()

        if tab_index == 0:
            if self.w_main.tabnavi.isTabEnabled(tab_count-1):
                self.w_main.tabnavi.setCurrentIndex(tab_count-1)
        else:
            self.w_main.tabnavi.setCurrentIndex(tab_index-1)


    def enableTabs(self):

        for i in range(1,3):
            self.w_main.tabnavi.setTabEnabled(i, True)


    def dissableTabs(self):

        for i in range(1,3):
            self.w_main.tabnavi.setTabEnabled(i, False)


    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.w_main.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == '&Log':
            self.data.run['log'].onShowTab()
        if cur_tab_name == '&Roadmap':
            self.data.run['roadmap'].onShowTab()

# vim: set ts=4 sw=4 ai si expandtab:

