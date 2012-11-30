#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxProject:
    
    def __init__(self, datastore):
        
        self.data = datastore

        # MAINWINDOW WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/project.ui')
        uifile.open(QFile.ReadOnly)
        self.widget = loader.load(uifile)
        uifile.close()
        
        """

        # setup new and edit dialog
        for obj, fname in (('diag_new', 'forms/project_diag_new.ui'),
                           ('diag_edit', 'forms/project_diag_edit.ui')):
            f = QFile(fname)
            f.open(QFile.ReadOnly)
            self.__dict__[obj] = loader.load(f)
            f.close()
            self.__dict__[obj].setParent(self.widget)
            self.__dict__[obj].setWindowFlags(Qt.Dialog)
        
        self.diag_new.accepted.connect(self.onSubmitNewProject)
        self.diag_edit.accepted.connect(self.onSubmitProjectEdit)
        self.diag_new.push_browse_path.clicked.connect(self.onBrowseNewPath)
        self.diag_edit.push_browse_path.clicked.connect(self.onBrowseEditPath)

        # setup table
        self.table = self.widget.table_project_list
        self.table_headers = [
             'Name', 'Project Type', 'Status', 'Category', 'Prio.', 'Chall.', 
             'Version', 'Last Changed', 'ID' ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)
        
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(4, 50)
        self.table.setColumnWidth(5, 50)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 160)
        self.table.setColumnWidth(8, 80)

        # CONNECT SIGNALS AND SLOTS
        self.widget.push_project_new.clicked.connect(self.showNewProjectDiag)
        self.widget.push_project_edit.clicked.connect(self.showEditProjectDiag)
        self.widget.push_project_delete.clicked.connect(self.onDeleteProject)
        self.widget.push_project_open.clicked.connect(self.data.load)
        self.widget.push_project_save.clicked.connect(self.data.save)

        """

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
        project['diag_new_detail'].clear()

        project['diag_new_name'].setFocus()

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
            QStandardItem('0.0'),
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
            (6, '0.0'), # FIXME: get this from milestones
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
                QStandardItem('0.0'), # FIXME: get this from milestones
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

