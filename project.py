#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxProject(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat
        
        rd['modules'].append('project')
        rd['project'] = {}
        rd['project']['changed'] = False
        rd['project']['savepath'] = ''

        sd['project'] = {}
        sd['project']['p'] = {}

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/project.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()

        parent_widget = rd['mainwindow']['tab_project']
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
        
        uifile = QFile('forms/project_diag_edit.ui')
        uifile.open(QFile.ReadOnly)
        edit_diag = loader.load(uifile)
        uifile.close()

        new_diag.setParent(rd['mainwindow']['ui'])
        new_diag.setWindowFlags(Qt.Dialog)
        edit_diag.setParent(rd['mainwindow']['ui'])
        edit_diag.setWindowFlags(Qt.Dialog)

        rd['project']['table_project_list'] = ui.table_project_list

        # SETUP PROJECT TABLE
        model = rd['project']['table_model_index'] = QStandardItemModel()
        headers = rd['project']['table_model_index_headers'] = \
            ['Name', 'Project Type', 'Status', 'Category', 'Prio.', 'Chall.', 
             'Version', 'Last Changed', 'ID' ]
        model.setHorizontalHeaderLabels(headers)
        rd['project']['table_project_list'].setModel(model)

        # POPULATE DATA INDEX
        sd['project']['lastid'] = 0

        rd['project']['ui'] = ui
        rd['project']['self'] = self
        rd['project']['push_open'] = ui.push_project_open
        rd['project']['push_save'] = ui.push_project_save
        rd['project']['push_new'] = ui.push_project_new
        rd['project']['push_edit'] = ui.push_project_edit
        rd['project']['push_delete'] = ui.push_project_delete

        rd['project']['diag_new'] = new_diag
        rd['project']['diag_new_name'] = new_diag.line_name
        rd['project']['diag_new_type'] = new_diag.combo_type
        rd['project']['diag_new_status'] = new_diag.combo_status
        rd['project']['diag_new_category'] = new_diag.combo_category
        rd['project']['diag_new_priority'] = new_diag.spin_priority
        rd['project']['diag_new_challenge'] = new_diag.spin_challenge
        rd['project']['diag_new_version'] = new_diag.line_version
        rd['project']['diag_new_basepath'] = new_diag.line_basepath
        rd['project']['diag_new_browse_path'] = new_diag.push_browse_path
        rd['project']['diag_new_detail'] =    new_diag.text_description
        
        rd['project']['diag_edit'] = edit_diag
        rd['project']['diag_edit_name'] = edit_diag.line_name
        rd['project']['diag_edit_type'] = edit_diag.combo_type
        rd['project']['diag_edit_status'] = edit_diag.combo_status
        rd['project']['diag_edit_category'] = edit_diag.combo_category
        rd['project']['diag_edit_priority'] = edit_diag.spin_priority
        rd['project']['diag_edit_challenge'] = edit_diag.spin_challenge
        rd['project']['diag_edit_version'] = edit_diag.line_version
        rd['project']['diag_edit_basepath'] = edit_diag.line_basepath
        rd['project']['diag_edit_browse_path'] = edit_diag.push_browse_path
        rd['project']['diag_edit_detail'] =    edit_diag.text_description
        
        rd['project'][':showNewProjectDiag'] = self.showNewProjectDiag
        rd['project'][':onSubmitNewProject'] = self.onSubmitNewProject
        rd['project'][':onBrowseNewPath'] = self.onBrowseNewPath
        rd['project'][':showEditProjectDiag'] = self.showEditProjectDiag
        rd['project'][':onSubmitProjectEdit'] = self.onSubmitProjectEdit
        rd['project'][':onBrowseEditPath'] = self.onBrowseEditPath
        rd['project'][':reset'] = self.reset
        rd['project'][':getSelectedProject'] = self.getSelectedProject
        rd['project'][':getActiveRow'] = self.getActiveRow
        rd['project'][':getSelectedProject'] = self.getSelectedProject
        rd['project'][':getSelectedProjectName'] = self.getSelectedProjectName
        rd['project'][':onDeleteProject'] = self.onDeleteProject
        rd['project'][':onSaveAs'] = self.onSaveAs
        rd['project'][':onSave'] = self.onSave
        rd['project'][':onOpen'] = self.onOpen
        rd['project'][':updateTimestamp'] = self.updateTimestamp

        # CONNECT SIGNALS AND SLOTS
        rd['project']['push_new'].clicked.connect(rd['project'][':showNewProjectDiag'])
        rd['project']['push_edit'].clicked.connect(rd['project'][':showEditProjectDiag'])
        rd['project']['push_delete'].clicked.connect(rd['project'][':onDeleteProject'])
        rd['project']['push_open'].clicked.connect(rd['project'][':onOpen'])
        rd['project']['diag_new'].accepted.connect(rd['project'][':onSubmitNewProject'])
        rd['project']['diag_edit'].accepted.connect(rd['project'][':onSubmitProjectEdit'])
        rd['project']['diag_new_browse_path'].clicked.connect(rd['project'][':onBrowseNewPath'])
        rd['project']['diag_edit_browse_path'].clicked.connect(rd['project'][':onBrowseEditPath'])
        rd['project']['push_save'].clicked.connect(rd['project'][':onSave'])

        table = rd['project']['table_project_list']
        table.setColumnWidth(0, 200)
        table.setColumnWidth(4, 50)
        table.setColumnWidth(5, 50)
        table.setColumnWidth(6, 80)
        table.setColumnWidth(7, 160)
        table.setColumnWidth(8, 80)

    ####################   UTILITY METHODS   #################### 

    def updateTimestamp(self, timestamp):

        # note: we assume that project is in active row
        
        rd = self.rundat
        table = rd['project']['table_project_list']
        model = rd['project']['table_model_index']
        s_project = self.savdat['project']['p'][self.getSelectedProject()]
        active_row = self.getActiveRow()
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        # update timestamp in savdat
        s_project['timestamp'] = timestamp

        # update timestamp in project index
        model.setItem(active_row, 7, QStandardItem(disptime))

    def getSelectedProject(self):

        rd = self.rundat

        table = rd['project']['table_project_list']
        model = rd['project']['table_model_index']

        row = table.currentIndex().row()
        index = model.index(row, 8)

        return int(model.itemFromIndex(index).text())

    def getSelectedProjectName(self):

        rd = self.rundat

        table = rd['project']['table_project_list']
        model = rd['project']['table_model_index']

        row = table.currentIndex().row()
        index = model.index(row, 0)
        return model.itemFromIndex(index).text()

    def getActiveRow(self):

        return self.rundat['project']['table_project_list'].currentIndex().row()

    ####################   METHODS   #################### 

    def showNewProjectDiag(self):

        project = self.rundat['project']

        # reset controls
        project['diag_new_name'].clear()
        project['diag_new_basepath'].clear()
        project['diag_new_type'].setCurrentIndex(0)
        project['diag_new_status'].setCurrentIndex(0)
        project['diag_new_category'].setCurrentIndex(0)
        project['diag_new_priority'].setValue(0)
        project['diag_new_challenge'].setValue(0)
        project['diag_new_version'].setText('0.0.0')
        project['diag_new_detail'].clear()

        # show widget
        project['diag_new'].show()

    def onSubmitNewProject(self):

        run_project = self.rundat['project']
        sav_project = self.savdat['project']

        # retrive data from dialog fields
        name = run_project['diag_new_name'].text()
        basepath = run_project['diag_new_basepath'].text()
        ptype = run_project['diag_new_type'].currentText()
        status = run_project['diag_new_status'].currentText()
        category = run_project['diag_new_category'].currentText()
        priority = run_project['diag_new_priority'].value()
        challenge = run_project['diag_new_challenge'].value()
        version = run_project['diag_new_version'].text()
        detail = run_project['diag_new_detail'].toPlainText()

        timestamp = int(time.time())

        # store data in savdat
        pid = sav_project['lastid']
        sav_project['p'][pid] = {}
        sav_project['p'][pid]['name']      = name
        sav_project['p'][pid]['basepath']  = basepath
        sav_project['p'][pid]['type']      = ptype
        sav_project['p'][pid]['status']    = status
        sav_project['p'][pid]['category']  = category
        sav_project['p'][pid]['priority']  = priority
        sav_project['p'][pid]['challenge'] = challenge
        sav_project['p'][pid]['version']   = version
        sav_project['p'][pid]['detail']    = detail
        sav_project['p'][pid]['timestamp'] = timestamp
        sav_project['lastid'] += 1
      
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        # instert row into table
        run_project['table_model_index'].insertRow(0, [
            QStandardItem(name),
            QStandardItem(ptype),
            QStandardItem(status),
            QStandardItem(category),
            QStandardItem(str(priority)),
            QStandardItem(str(challenge)),
            QStandardItem(version),
            QStandardItem(disptime),
            QStandardItem(str(pid))
            ])

        # enable controls
        run_project['table_project_list'].selectRow(0)
        run_project['table_project_list'].setFocus()

        self.rundat['mainwindow'][':enableTabs']()

        run_project['push_edit'].setEnabled(True)
        run_project['push_delete'].setEnabled(True)
        run_project['push_save'].setEnabled(True)

        run_project['changed'] = True

    def onOpen(self):

        sd = self.savdat
        rd = self.rundat

        if rd['project']['changed']:
            response = QMessageBox.question(
            rd['project']['ui'],
            'Discard changes?',
            'Opening a file will discard your changes. Do you want to proceed?',
            QMessageBox.Yes|QMessageBox.No)

            if response == QMessageBox.StandardButton.No:
                return

        rd['project']['savepath'] = QFileDialog.getOpenFileName(
            rd['project']['ui'], 
            'Open projects', 
            os.path.expanduser('~/Documents'), 
            'Nelia Files (*.spt)')[0]

        # path dialog aborted
        if rd['project']['savepath'] == '':
            return
        
        file_buffer = ''
        with open(rd['project']['savepath'], 'rb') as f:
                file_buffer = f.read()

        decompressed = gzip.decompress(file_buffer)
        sd = pickle.loads(decompressed)

        # update savedat
        rd['mainwindow']['self'].savdat = sd
        rd['project']['self'].savdat = sd
        rd['log']['self'].savdat = sd

        # reload project list
        self.reset()
        rd['log'][':reset']()

    def onSave(self):

        sd = self.savdat
        rd = self.rundat

        if rd['project']['savepath'] == '':
            self.onSaveAs()

        # save as dialog aborted
        if rd['project']['savepath'] == '.spt':
            return

        pickled_data = pickle.dumps(sd, 3)
        compressed_data = gzip.compress(pickled_data)

        with open(rd['project']['savepath'], 'wb') as f:
            f.write(compressed_data)
        
        rd['project']['changed'] = False

    def onSaveAs(self):

        rd = self.rundat

        file_name = QFileDialog.getSaveFileName(
            rd['project']['ui'], 
            'Save projects', 
            os.path.expanduser('~/Documents/save.spt'), 
            'Nelia Files (*.spt)')[0]

        if file_name.rfind('.spt') != len(file_name) - 4:
            file_name += '.spt'

        rd['project']['savepath'] = file_name

        self.onSave()

    def onDeleteProject(self):

        sd = self.savdat
        rd = self.rundat

        pid = self.getSelectedProject()
        row = self.getActiveRow()

        response = QMessageBox.question(
            rd['project']['ui'],
            'Delete project?',
            'Delete project ' + str(pid) + '?',
            QMessageBox.Yes|QMessageBox.No)

        if response == QMessageBox.StandardButton.No:
            return

        del sd['project']['p'][pid]
        rd['project']['table_model_index'].removeRow(row)
        
        rd['project']['changed'] = True

    def setComboValue(self, combo, text):

        combo.setCurrentIndex(combo.findText(text))

    def showEditProjectDiag(self):

        sd = self.savdat
        rd = self.rundat

        pid = self.getSelectedProject()

        rd['project']['diag_edit_name'].setText(sd['project']['p'][pid]['name'])
        rd['project']['diag_edit_basepath'].setText(sd['project']['p'][pid]['basepath'])
        rd['project']['diag_edit_version'].setText(sd['project']['p'][pid]['version'])
        self.setComboValue(rd['project']['diag_edit_type'], sd['project']['p'][pid]['type'])
        self.setComboValue(rd['project']['diag_edit_status'], sd['project']['p'][pid]['status'])
        self.setComboValue(rd['project']['diag_edit_category'], sd['project']['p'][pid]['category'])
        rd['project']['diag_edit_priority'].setValue(sd['project']['p'][pid]['priority'])
        rd['project']['diag_edit_challenge'].setValue(sd['project']['p'][pid]['challenge'])
        rd['project']['diag_edit_detail'].setPlainText(sd['project']['p'][pid]['detail'])

        rd['project']['diag_edit'].show()

    def onBrowseEditPath(self):

        self.rundat['project']['diag_edit_basepath'].setText( 
            QFileDialog.getExistingDirectory(
            self.rundat['project']['diag_edit'],
            'Choose project base path',
            os.path.expanduser('~')))

    def onBrowseNewPath(self):

        self.rundat['project']['diag_new_basepath'].setText( 
            QFileDialog.getExistingDirectory(
            self.rundat['project']['diag_new'],
            'Choose project base path',
            os.path.expanduser('~')))

    def onSubmitProjectEdit(self):
        
        sd = self.savdat
        rd = self.rundat

        pid = self.getSelectedProject()
        timestamp = int(time.time())

        sd['project']['p'][pid]['name'] = rd['project']['diag_edit_name'].text()
        sd['project']['p'][pid]['basepath'] = rd['project']['diag_edit_basepath'].text()
        sd['project']['p'][pid]['type'] = rd['project']['diag_edit_type'].currentText()
        sd['project']['p'][pid]['status'] = rd['project']['diag_edit_status'].currentText()
        sd['project']['p'][pid]['category'] = rd['project']['diag_edit_category'].currentText()
        sd['project']['p'][pid]['priority'] = rd['project']['diag_edit_priority'].value()
        sd['project']['p'][pid]['challenge'] = rd['project']['diag_edit_challenge'].value()
        sd['project']['p'][pid]['version'] = rd['project']['diag_edit_version'].text()
        sd['project']['p'][pid]['detail'] = rd['project']['diag_edit_detail'].toPlainText()
        sd['project']['p'][pid]['timestamp'] = timestamp
        
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        tabdat = (
            (0, rd['project']['diag_edit_name'].text()),
            (1, rd['project']['diag_edit_type'].currentText()),
            (2, rd['project']['diag_edit_status'].currentText()),
            (3, rd['project']['diag_edit_category'].currentText()),
            (4, rd['project']['diag_edit_priority'].value()),
            (5, rd['project']['diag_edit_challenge'].value()),
            (6, rd['project']['diag_edit_version'].text()),
            (7, disptime),
            (8, str(pid))
        )

        model = rd['project']['table_model_index']

        for index, value in tabdat:
            model.setData(
                model.index(self.getActiveRow(), index), value)
    
        rd['project']['table_project_list'].setFocus()
        rd['project']['changed'] = True

    def reset(self):

        sd = self.savdat
        rd = self.rundat

        model = rd['project']['table_model_index']

        model.clear()
        model.setHorizontalHeaderLabels(rd['project']['table_model_index_headers'])

        table = rd['project']['table_project_list']
        table.setColumnWidth(0, 200)
        table.setColumnWidth(4, 50)
        table.setColumnWidth(5, 50)
        table.setColumnWidth(6, 80)
        table.setColumnWidth(7, 160)
        table.setColumnWidth(8, 80)

        for pid,project in sd['project']['p'].items():
            disptime = datetime.datetime.fromtimestamp(project['timestamp']).isoformat()
            rd['project']['table_model_index'].insertRow(0, [
                QStandardItem(project['name']),
                QStandardItem(project['type']),
                QStandardItem(project['status']),
                QStandardItem(project['category']),
                QStandardItem(str(project['priority'])),
                QStandardItem(str(project['challenge'])),
                QStandardItem(project['version']),
                QStandardItem(disptime),
                QStandardItem(str(pid))
            ])
        
        rd['project']['table_project_list'].selectRow(0)
        rd['project']['table_project_list'].setFocus()
        
        rd['mainwindow'][':enableTabs']()
        rd['project']['push_edit'].setEnabled(True)
        rd['project']['push_delete'].setEnabled(True)
        rd['project']['push_save'].setEnabled(True)

        rd['project']['changed'] = False

# vim: set ts=4 sw=4 ai si expandtab:

