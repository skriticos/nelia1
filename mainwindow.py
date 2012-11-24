#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject
from log import NxLog
from roadmap import NxRoadmap

class MainWindow(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat

        rd['modules'].append('mainwindow')
        rd['mainwindow'] = {}
        sd['mainwindow'] = {}

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/mainwindow.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()
        ui.setWindowIcon(QIcon('img/nelia-icon32.png'))
        ui.setGeometry(100,70,1000,600)
      
        # POPULATE DATA INDEX
        rd['mainwindow']['ui'] = ui
        rd['mainwindow']['self'] = self
        rd['mainwindow']['tabwidget_main'] = ui.tabwidget_main
        rd['mainwindow']['tab_project'] = ui.tab_project
        rd['mainwindow']['tab_log'] = ui.tab_log
        rd['mainwindow']['tab_roadmap'] = ui.tab_roadmap
        rd['mainwindow'][':show'] = self.show
        rd['mainwindow'][':tabChanged'] = self.tabChanged
        rd['mainwindow'][':enableTabs'] = self.enableTabs
        rd['mainwindow'][':dissableTabs'] = self.dissableTabs
        rd['mainwindow'][':onTabForward'] = self.onTabForward
        rd['mainwindow'][':onTabBackward'] = self.onTabBackward

        # DISSABLE TABS UNTIL PROJECT SELECTED
        self.dissableTabs()
        
        # INITIATE CHILD WIDGETS
        project = NxProject(sd, rd)
        log = NxLog(sd, rd)
        roadmap = NxRoadmap(sd, rd)
       
        # CONNECT SIGNALS AND SLOTS
        rd['mainwindow']['tabwidget_main'].currentChanged.connect(rd['mainwindow'][':tabChanged'])

        # close window shortcut
        close_window_shortcut = QShortcut(QKeySequence('Ctrl+w'), ui)
        close_window_shortcut.activated.connect(ui.close)

        switch_widget_forward = QShortcut(QKeySequence('Ctrl+PgUp'), ui)
        switch_widget_forward.activated.connect(rd['mainwindow'][':onTabForward'])
        
        switch_widget_backward = QShortcut(QKeySequence('Ctrl+PgDown'), ui)
        switch_widget_backward.activated.connect(rd['mainwindow'][':onTabBackward'])

        QObject.installEventFilter(ui, self)

    def eventFilter(self, obj, event):

        if obj == self.rundat['mainwindow']['ui']:
            if isinstance(event, QCloseEvent):
                print ('closing window')
                print ('note: implement closing routine')

        res = False
        try:
            res = QObject.eventFilter(self.rundat['mainwindow']['ui'], obj, event)
        except:
            pass
        return res

    def onTabForward(self):

        # get current tab index
        tab_index = self.rundat['mainwindow']['tabwidget_main'].currentIndex()

        # get max index
        tab_count = self.rundat['mainwindow']['tabwidget_main'].count()

        # next tab
        if tab_index+1 == tab_count:
            self.rundat['mainwindow']['tabwidget_main'].setCurrentIndex(0)
        elif self.rundat['mainwindow']['tabwidget_main'].isTabEnabled(tab_index+1):
            self.rundat['mainwindow']['tabwidget_main'].setCurrentIndex(tab_index+1)

    def onTabBackward(self):
        
        # get current tab index
        tab_index = self.rundat['mainwindow']['tabwidget_main'].currentIndex()

        # get max index
        tab_count = self.rundat['mainwindow']['tabwidget_main'].count()
        
        if tab_index == 0:
            if self.rundat['mainwindow']['tabwidget_main'].isTabEnabled(tab_count-1):
                self.rundat['mainwindow']['tabwidget_main'].setCurrentIndex(tab_count-1)
        else:
            self.rundat['mainwindow']['tabwidget_main'].setCurrentIndex(tab_index-1)

    def enableTabs(self):

        for i in range(1,3):
            self.rundat['mainwindow']['tabwidget_main'].setTabEnabled(i, True)

    def dissableTabs(self):
        
        for i in range(1,3):
            self.rundat['mainwindow']['tabwidget_main'].setTabEnabled(i, False)

    def show(self):

        self.rundat['mainwindow']['ui'].show()

    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.rundat['mainwindow']['tabwidget_main']
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        if cur_tab_name == 'Log':
            self.rundat['log'][':onShowTab']()
        if cur_tab_name == 'Roadmap':
            self.rundat['roadmap'][':onShowTab']()

# vim: set ts=4 sw=4 ai si expandtab:

