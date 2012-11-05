#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from project import NxProject

class MainWindow(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        self.savdat = savdat
        self.rundat = rundat

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/mainwindow.ui')
        uifile.open(QFile.ReadOnly)
        self.ui = loader.load(uifile)
        uifile.close()
        self.ui.setWindowIcon(QIcon('img/icon.png'))
      
        # POPULATE DATA INDEX
        rundat['modules'].append('mainwindow')
        rundat['mainwindow'] = self
        rundat['mainwindow.ui'] = self.ui
        rundat['mainwindow.tabwidget_main'] = self.ui.tabwidget_main
        rundat['mainwindow.tab_project'] = self.ui.tab_project
        rundat['mainwindow:show'] = self.show
        rundat['mainwindow:tabChanged'] = self.tabChanged
        
        # INITIATE CHILD WIDGETS
        self.project = NxProject(savdat, rundat)
       
        # CONNECT SIGNALS AND SLOTS
        rundat['mainwindow.tabwidget_main'].currentChanged.connect(rundat['mainwindow:tabChanged'])

        # FOR DEBUGGING (UNTIL WE HAVE DEBUG LOG)
        from pprint import pprint
        pprint(savdat)
        pprint(rundat)

    def show(self):

        self.ui.show()

    def tabChanged(self):

        # PREPARE DATA
        tab_widget = self.rundat['mainwindow.tabwidget_main']
        cur_tab_name = tab_widget.tabText(tab_widget.currentIndex())

        # ACT ON CHANGE
        print('stub')
        print('tab_changed', tab_widget, cur_tab_name)


# vim: set ts=4 sw=4 ai si expandtab:

