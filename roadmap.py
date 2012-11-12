#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxRoadmap(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat
        
        rd['modules'].append('roadmap')
        rd['roadmap'] = {}

        sd['roadmap'] = {}          # roadmap save base
        sd['roadmap']['p'] = {}     # roadmap for projects
        rd['roadmap']['last_roadmap_pid'] = None    # to check if reload roadmap on tab change necessary

        run_roadmap = rd['roadmap']
        sav_roadmap = sd['roadmap']

        # mainwindow widget setup
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/roadmap.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()

        parent_widget = rd['mainwindow']['tab_roadmap']
        ui.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(ui, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)
        
        # pre-populate data index
        run_roadmap['ui'] = ui
        run_roadmap['self'] = self

        run_roadmap[':reset'] = self.reset
        run_roadmap[':onShowTab'] = self.onShowTab

    ####################   METHODS   #################### 

    def onShowTab(self):

        run_roadmap = self.rundat['roadmap']
        sav_roadmap = self.savdat['roadmap']

        pid = self.rundat['project'][':getSelectedProject']()

    def reset(self):
    
        # ensure roadmap is reloaded when switched to after opening
        self.rundat['roadmap']['last_roadmap_pid'] = None

# vim: set ts=4 sw=4 ai si expandtab:

