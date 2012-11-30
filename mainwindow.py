#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject
from log import NxLog
from roadmap import NxRoadmap

from datastore import DataStore

class MainWindow(QObject):

    """
        The main window control class contains the application main
        container window and container tab widget. It commands global
        actions, like tab switching, exit handling, saving and loading.
    """

    # TODO: Move save/load core routines to this widget (from project)

    def __init__(self, argv):

        super().__init__()

        # Load UI file for main window.
        # This contains the base window and the tabs and acts as primary
        # container.
        loader = QtUiTools.QUiLoader()
        widgetfile = QFile('forms/mainwindow.ui')
        widgetfile.open(QFile.ReadOnly)
        self.widget = loader.load(widgetfile)
        widgetfile.close()
        self.widget.setWindowIcon(QIcon('img/nelia-icon32.png'))
        self.widget.setGeometry(100,70,1000,600)
        
        # initialize data store
        self.data = DataStore(self.widget)
        self.data.run['mainwin'] = self


        # Interesting widgets in mainwindow.ui:
        # . tabnavi
        # . tab_project
        # . tab_log
        # . tab_roadmap

        # Dissable all tabs except the project tab.
        # They show the data from the selected project, and are in undefined
        # before a selection is made.
        self.dissableTabs()

        # Add child widgets.
        # TODO: move widget embedding to the main window for the child widgets.
        project = NxProject(self.data)
        
        project.widget.setParent(self.widget.tab_project)
        grid = QGridLayout()
        grid.addWidget(project.widget, 0, 0)
        grid.setContentsMargins(10, 10, 10, 10)
        self.widget.tab_project.setLayout(grid)

        '''
        log     = NxLog     (self.data)
        roadmap = NxRoadmap (self.data)
        '''

        # Connect signals and slots.
        self.widget.tabnavi.currentChanged.connect(self.tabChanged)

        # Global shortcuts:
        close_shortcut = QShortcut(QKeySequence('Ctrl+w'), self.widget)
        close_shortcut.activated.connect(self.widget.close)
        switch_forward = QShortcut(QKeySequence('Ctrl+PgUp'), self.widget)
        switch_forward.activated.connect(self.onTabForward)
        switch_backward = QShortcut(QKeySequence('Ctrl+PgDown'), self.widget)
        switch_backward.activated.connect(self.onTabBackward)
        save = QShortcut(QKeySequence('Ctrl+s'), self.widget)
        save.activated.connect(self.data.save)

        # Intercept close event (see self.eventFilter).
        QObject.installEventFilter(self.widget, self)


    def eventFilter(self, obj, event):

        """
            Capture main window close event.
            This might be caused by the user clicking the (x) window button or by
            exiting via the Ctrl-w shortcut (or any other way that tells the main
            window to close).
        """

        if obj == self.widget:
            if isinstance(event, QCloseEvent):
                # TODO: handle close window (e.g. show warning, offer to save)
                pass
        res = False
        try:
            res = QObject.eventFilter(self.widget, obj, event)
        except:
            pass
        return res


    def onTabForward(self):

        # get current tab index
        tab_index = self.widget.tabnavi.currentIndex()

        # get max index
        tab_count = self.widget.tabnavi.count()

        # next tab
        if tab_index+1 == tab_count:
            self.widget.tabnavi.setCurrentIndex(0)
        elif self.widget.tabnavi.isTabEnabled(tab_index+1):
            self.widget.tabnavi.setCurrentIndex(tab_index+1)


    def onTabBackward(self):

        # get current tab index
        tab_index = self.widget.tabnavi.currentIndex()

        # get max index
        tab_count = self.widget.tabnavi.count()

        if tab_index == 0:
            if self.widget.tabnavi.isTabEnabled(tab_count-1):
                self.widget.tabnavi.setCurrentIndex(tab_count-1)
        else:
            self.widget.tabnavi.setCurrentIndex(tab_index-1)


    def enableTabs(self):

        for i in range(1,3):
            self.widget.tabnavi.setTabEnabled(i, True)


    def dissableTabs(self):

        for i in range(1,3):
            self.widget.tabnavi.setTabEnabled(i, False)


    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.widget.tabnavi
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == 'Log':
            self.data.run['log'].onShowTab()
        if cur_tab_name == 'Roadmap':
            self.data.run['roadmap'].onShowTab()

# vim: set ts=4 sw=4 ai si expandtab:

