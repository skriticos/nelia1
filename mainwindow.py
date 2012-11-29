#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject
from log import NxLog
from roadmap import NxRoadmap

import pickle, gzip


class DataStore:

    """
        This class will contain all data that will be stored.
        It takes care of saving and loading. If no path is specified
        yet, it will prompt for one, if not already present and not
        passed
    """

    version = 1
    app_name = 'Nelia'

    def __init__(self):

        self.path = None
        self.project = {    # Project data
            'nextid': 1
        }
        self.log = {}       # Log data
        self.roadmap = {}   # Roadmap data
        self.run = {}       # Shared runtime data, not saved

    def reset(self):

        del self.run
        self.run = {
            'changed':          True, # global, if anything changes (bool)
            'sel_project':      None, # selected project (i)
            'curr_milestone':   None, # last completed milestone (x,y)
            'next_milestone':   None, # next milestone     (x,y)
            'sel_milestone':    None  # selected milestone (m,n)
        }

    def save(self, path=None):

		# TODO:
		# 1. if no path specifide -> prompt for path
        #    -> abort, if no path is selected

        data = {
            'meta': {
                'version': version,
                'app_name': app_name
            },
            'projcet': self.project,
            'log': self.log,
            'roadmap': self.roadmap
        }

		# TODO:
		# 2. save data


    def load(self, path=None):

		# TODO:
		# 1. if no path specifide -> prompt for path
        #    -> abort, if no path is selected
		# 2. load data to data

        self.path       = path

        del self.projects
        del self.log
        del self.roadmap

        self.projects   = data['project']
        self.log        = data['log']
        self.roadmap    = data['roadmap']


class MainWindow(QObject):

    """
        The main window control class contains the application main
        container window and container tab widget. It commands global
        actions, like tab switching, exit handling, saving and loading.
    """

    # TODO: Move save/load core routines to this widget (from project)

    def __init__(self):

        super().__init__()

        self.data = DataStore()
        self.data.run['mainwin'] = self

        # Load UI file for main window.
        # This contains the base window and the tabs and acts as primary
        # container.
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/mainwindow.ui')
        uifile.open(QFile.ReadOnly)
        self.widget = loader.load(self.widgetfile)
        self.widgetfile.close()
        self.widget.setWindowIcon(QIcon('img/nelia-icon32.png'))
        self.widget.setGeometry(100,70,1000,600)

        # Interesting widgets in mainwindow.ui:
        # . tabwidget_main
        # . tab_project
        # . tab_log
        # . tab_roadmap

        # Dissable all tabs except the project tab.
        # They show the data from the selected project, and are in undefined
        # before a selection is made.
        self.dissableTabs()

        # Add child widgets.
        # TODO: move widget embedding to the main window for the child widgets.
        project = NxProject (self.data)
        log     = NxLog     (self.data)
        roadmap = NxRoadmap (self.data)

        # Connect signals and slots.
        self.widget.tabwidget_main.currentChanged.connect(self.tabChanged)

        # Global shortcuts:
        close_shortcut = QShortcut(QKeySequence('Ctrl+w'), self.widget)
        close_shortcut.activated.connect(self.widget.close)
        switch_forward = QShortcut(QKeySequence('Ctrl+PgUp'), self.widget)
        switch_forward.activated.connect(self.onTabForward)
        switch_backward = QShortcut(QKeySequence('Ctrl+PgDown'), self.widget)
        switch_backward.activated.connect(self.onTabBackward)

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
        res = False
        try:
            res = QObject.eventFilter(self.widget, obj, event)
        except:
            pass
        return res


    def onTabForward(self):

        # get current tab index
        tab_index = self.widget.tabwidget_main.currentIndex()

        # get max index
        tab_count = self.widget.tabwidget_main.count()

        # next tab
        if tab_index+1 == tab_count:
            self.widget.tabwidget_main.setCurrentIndex(0)
        elif self.widget.tabwidget_main.isTabEnabled(tab_index+1):
            self.widget.tabwidget_main.setCurrentIndex(tab_index+1)


    def onTabBackward(self):

        # get current tab index
        tab_index = self.widget.tabwidget_main.currentIndex()

        # get max index
        tab_count = self.widget.tabwidget_main.count()

        if tab_index == 0:
            if self.widget.tabwidget_main.isTabEnabled(tab_count-1):
                self.widget.tabwidget_main.setCurrentIndex(tab_count-1)
        else:
            self.widget.tabwidget_main.setCurrentIndex(tab_index-1)


    def enableTabs(self):

        for i in range(1,3):
            self.widget.tabwidget_main.setTabEnabled(i, True)


    def dissableTabs(self):

        for i in range(1,3):
            self.widget.tabwidget_main.setTabEnabled(i, False)


    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.widget.tabwidget_main
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == 'Log':
            self.data.run['log'].onShowTab()
        if cur_tab_name == 'Roadmap':
            self.data.run['roadmap'].onShowTab()

# vim: set ts=4 sw=4 ai si expandtab:

