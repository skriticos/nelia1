#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject

class MainWindow(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/mainwindow.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()
        ui.setWindowIcon(QIcon('img/icon.png'))
      
        # POPULATE DATA INDEX
        rd['modules'].append('mainwindow')
        rd['mainwindow'] = self
        rd['mainwindow.ui'] = ui
        rd['mainwindow.tabwidget_main'] = ui.tabwidget_main
        rd['mainwindow.tab_project'] = ui.tab_project
        rd['mainwindow.tab_log'] = ui.tab_log
        rd['mainwindow.tab_data'] = ui.tab_data
        rd['mainwindow.tab_workflow'] = ui.tab_workflow
        rd['mainwindow.tab_roadmap'] = ui.tab_roadmap
        rd['mainwindow.tab_repository'] = ui.tab_repository
        rd['mainwindow:show'] = self.show
        rd['mainwindow:tabChanged'] = self.tabChanged
        rd['mainwindow:enableTabs'] = self.enableTabs
        rd['mainwindow:dissableTabs'] = self.dissableTabs

        # DISSABLE TABS UNTIL PROJECT SELECTED
        self.dissableTabs()
        
        # INITIATE CHILD WIDGETS
        project = NxProject(sd, rd)
       
        # CONNECT SIGNALS AND SLOTS
        rd['mainwindow.tabwidget_main'].currentChanged.connect(rd['mainwindow:tabChanged'])

        # FOR DEBUGGING (UNTIL WE HAVE DEBUG LOG)
        from pprint import pprint
        pprint(savdat)
        pprint(rundat)

    def enableTabs(self):

        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(1, True)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(2, True)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(3, True)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(4, True)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(5, True)

    def dissableTabs(self):
        
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(1, False)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(2, False)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(3, False)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(4, False)
        self.rundat['mainwindow.tabwidget_main'].setTabEnabled(5, False)

    def show(self):

        self.rundat['mainwindow.ui'].show()

    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.rundat['mainwindow.tabwidget_main']
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        # ACT ON CHANGE
        print('stub')
        print('tab_changed', tab_widget, cur_tab_name)


# vim: set ts=4 sw=4 ai si expandtab:

