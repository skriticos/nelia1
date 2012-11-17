#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

"""
roadmap prefixes:
    rmap = roadmap widget
    rmm  = roadmap milestone manage
    fil  = generic feature/issue list
    af   = add feature
    ai   = add issue
"""

class NxRoadmap(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        self.savdat = savdat
        self.rundat = rundat
        
        self.rundat['roadmap'] = {'last_roadmap_pid': None}  # roadmap save base

        # roadmap main widget, prefix: rmap == ui
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/roadmap.ui')
        uifile.open(QFile.ReadOnly)
        self.roadmap = loader.load(uifile)
        uifile.close()

        parent_widget = self.rundat['mainwindow']['tab_roadmap']
        self.roadmap.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(self.roadmap, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)

        self.rundat['roadmap'][':onShowTab'] = self.onShowTab
        
    ####################   METHODS   #################### 

    def onShowTab(self):

        pid = self.rundat['project'][':getSelectedProject']()
        
        # project selection changed or new project
        if self.rundat['roadmap']['last_roadmap_pid'] == None \
                or self.rundat['roadmap']['last_roadmap_pid'] != pid:

            self.rundat['roadmap']['selected_milestone'] = 1

            """
            # create pid data if not already done
            if pid not in self.savdat['roadmap']:

                pass
                # setup initial mata strucutre
                self.savdat['roadmap']['p'][pid] = {
                    'current_milestone': 0,
                    'next_new_milestone': 2,
                    'next_new_feature': 1,
                    'next_new_issue': 1,
                    1: {'name':'0.1', 'next':0, 'features': {}, 'issues': {} }
                }
            """

            # new pid, reset view!
            project_name = self.rundat['project'][':getSelectedProjectName']()

            self.roadmap.rmap_line_project.setText(project_name)

    def reset(self, savdat):
    
        self.savdat = savdat

        # ensure roadmap is reloaded when switched to after opening
        self.rundat['roadmap']['last_roadmap_pid'] = None


# vim: set ts=4 sw=4 ai si expandtab:

