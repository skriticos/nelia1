#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxProject(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        self.savdat = savdat
        self.rundat = rundat

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/project.ui')
        uifile.open(QFile.ReadOnly)
        self.ui = loader.load(uifile)
        uifile.close()

        parent_widget = rundat['mainwindow.tab_project']
        self.ui.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(self.ui, 0, 0)
        grid.setContentsMargins(0, 0, 0, 0)
        parent_widget.setLayout(grid)

        # NEW PROJECT DIALOG SETUP
        uifile = QFile('forms/project_diag_new.ui')
        uifile.open(QFile.ReadOnly)
        self.new_diag = loader.load(uifile)
        uifile.close()

        self.new_diag.setParent(rundat['mainwindow.ui'])
        self.new_diag.setWindowFlags(Qt.Dialog)

        # POPULATE DATA INDEX
        rundat['modules'].append('project')
        rundat['project'] = self
        rundat['project.ui'] = self.ui
        rundat['project.table_project_list'] = self.ui.table_project_list
        rundat['project.push_project_new'] = self.ui.push_project_new
        rundat['project.push_edit'] = self.ui.push_project_edit
        rundat['project.push_delete'] = self.ui.push_project_delete
        rundat['project.push_details'] = self.ui.push_project_details
        rundat['project.diag_new'] = self.new_diag
        rundat['project.diag_new_name'] = self.new_diag.line_name
        rundat['project.diag_new_type'] = self.new_diag.combo_type
        rundat['project.diag_new_category'] = self.new_diag.combo_category
        rundat['project.diag_new_priority'] = self.new_diag.spin_priority
        rundat['project.diag_new_challenge'] = self.new_diag.spin_challenge
        rundat['project.diag_new_basepath'] = self.new_diag.line_basepath
        rundat['project.diag_new_browse_path'] = self.new_diag.push_browse_path

        # CONNECT SIGNALS AND SLOTS
        rundat['project.push_project_new'].clicked.connect(self.showNewProjectDiag)

    def showNewProjectDiag(self):

        # RESET CONTROLS
        # SHOW WIDGET
        self.new_diag.show()

# vim: set ts=4 sw=4 ai si expandtab:

