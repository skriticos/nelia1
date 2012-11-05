#! /usr/bin/env python3

import os, time
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxProject(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/project.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()

        parent_widget = rd['mainwindow.tab_project']
        ui.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(ui, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)

        # NEW PROJECT DIALOG SETUP
        uifile = QFile('forms/project_diag_new.ui')
        uifile.open(QFile.ReadOnly)
        new_diag = loader.load(uifile)
        uifile.close()

        new_diag.setParent(rd['mainwindow.ui'])
        new_diag.setWindowFlags(Qt.Dialog)

        rd['project.table_project_list'] = ui.table_project_list

        # SETUP PROJECT TABLE
        model = rd['project.table_model_index'] = QStandardItemModel()
        headers = rd['project.table_model_index_headers'] = \
            ['Name', 'Project Type', 'Status', 'Category', 'Priority', 'Challenge', 
             'Version', 'Last Changed', 'ID' ]
        model.setHorizontalHeaderLabels(headers)
        rd['project.table_project_list'].setModel(model)

        # POPULATE DATA INDEX
        sd['project.lastid'] = 0

        rd['project.ui'] = ui
        rd['modules'].append('project')
        rd['project'] = self
        rd['project.push_open'] = ui.push_project_open
        rd['project.push_save'] = ui.push_project_save
        rd['project.push_saveas'] = ui.push_project_saveas
        rd['project.push_new'] = ui.push_project_new
        rd['project.push_edit'] = ui.push_project_edit
        rd['project.push_delete'] = ui.push_project_delete
        rd['project.push_details'] = ui.push_project_details
        rd['project.diag_new'] = new_diag
        rd['project.diag_new_name'] = new_diag.line_name
        rd['project.diag_new_type'] = new_diag.combo_type
        rd['project.diag_new_category'] = new_diag.combo_category
        rd['project.diag_new_priority'] = new_diag.spin_priority
        rd['project.diag_new_challenge'] = new_diag.spin_challenge
        rd['project.diag_new_basepath'] = new_diag.line_basepath
        rd['project.diag_new_browse_path'] = new_diag.push_browse_path
        rd['project:showNewProjectDiag'] = self.showNewProjectDiag
        rd['project:onNewProjectDiag'] = self.onNewProjectDiag
        rd['project:onBrowseNewPath'] = self.onBrowseNewPath
        rd['project:addProject'] = self.addProject
        rd['project:reset'] = self.reset

        # CONNECT SIGNALS AND SLOTS
        rd['project.push_new'].clicked.connect(rd['project:showNewProjectDiag'])
        rd['project.diag_new'].accepted.connect(rd['project:onNewProjectDiag'])
        rd['project.diag_new_browse_path'].clicked.connect(rd['project:onBrowseNewPath'])

    def showNewProjectDiag(self):

        rd = self.rundat

        # RESET CONTROLS
        rd['project.diag_new_name'].clear()
        rd['project.diag_new_basepath'].clear()
        rd['project.diag_new_type'].setCurrentIndex(0)
        rd['project.diag_new_category'].setCurrentIndex(0)
        rd['project.diag_new_priority'].setValue(0)
        rd['project.diag_new_challenge'].setValue(0)

        # SHOW WIDGET
        rd['project.diag_new'].show()

    def onBrowseNewPath(self):

        # callback for the path chooser in the create new project dialog

        self.rundat['project.diag_new_basepath'].setText( 
            QFileDialog.getExistingDirectory(
            self.rundat['project.diag_new'],
            'Choose project base path',
            os.path.expanduser('~')))
        
    def onNewProjectDiag(self):

        rd = self.rundat

        self.addProject(
            rd['project.diag_new_name'].text(),
            rd['project.diag_new_basepath'].text(),
            rd['project.diag_new_type'].currentText(),
            rd['project.diag_new_category'].currentText(),
            rd['project.diag_new_priority'].value(),
            rd['project.diag_new_challenge'].value())

    def addProject(self, name, basepath, ptype, category, priority, challenge):

        sd = self.savdat
        rd = self.rundat

        timestamp = int(time.time())

        # store data in savdat
        pid = str(sd['project.lastid'])
        sd['project.'+pid+'.name']      = name
        sd['project.'+pid+'.basepath']  = basepath
        sd['project.'+pid+'.type']      = ptype
        sd['project.'+pid+'.category']  = category
        sd['project.'+pid+'.priority']  = priority
        sd['project.'+pid+'.challenge'] = challenge
        sd['project.'+pid+'.timestamp'] = timestamp
        sd['project.lastid'] += 1
        
        # instert row into table
        rd['project.table_model_index'].insertRow(0, [
            QStandardItem(name),
            QStandardItem(ptype),
            QStandardItem('Spark'),
            QStandardItem(category),
            QStandardItem(str(priority)),
            QStandardItem(str(challenge)),
            QStandardItem('0.0.0'),
            QStandardItem(str(timestamp)),
            QStandardItem(pid)
        ])

        rd['project.table_project_list'].selectRow(0)
        rd['project.table_project_list'].setFocus()

        rd['mainwindow:enableTabs']()
        rd['project.push_edit'].setEnabled(True)
        rd['project.push_delete'].setEnabled(True)
        rd['project.push_details'].setEnabled(True)

        # TODO: add log entry

    def reset(self, savdat):

        pass

# vim: set ts=4 sw=4 ai si expandtab:

