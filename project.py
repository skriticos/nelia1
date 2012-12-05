#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import os, datetime, time

class NxProject:
    
    def __init__(self, parent, datastore, widget):
        
        self.parent = parent
        self.data   = datastore
        self.widget = widget

        # show new project dialog
        self.widget.push_project_new.clicked.connect(
            lambda: (
            parent.w_project_diag_new.line_name.clear(), 
            parent.w_project_diag_new.combo_ptype.setCurrentIndex(0), 
            parent.w_project_diag_new.combo_status.setCurrentIndex(0), 
            parent.w_project_diag_new.combo_category.setCurrentIndex(0), 
            parent.w_project_diag_new.spin_priority.setValue(0), 
            parent.w_project_diag_new.spin_challenge.setValue(0), 
            parent.w_project_diag_new.line_basepath.clear(), 
            parent.w_project_diag_new.text_description.clear(), 
            parent.w_project_diag_new.line_name.setFocus(), 
            parent.w_project_diag_new.show()))

        parent.w_project_diag_new.push_browse_path.clicked.connect(
            lambda: parent.w_project_diag_new.line_basepath.setText(
                QFileDialog.getExistingDirectory(
                    parent.w_project_diag_new, 'Choose project base path', os.path.expanduser('~'))))

        # show edit project dialog
        self.widget.push_project_edit.clicked.connect(self.showEditProject)
        
        parent.w_project_diag_edit.push_browse_path.clicked.connect(
            lambda: parent.w_project_diag_edit.line_basepath.setText(
                QFileDialog.getExistingDirectory(
                    self.data.run['w_project_diag_edit'], 'Choose project base path', os.path.expanduser('~'))))

        self.data.run['w_project_diag_new'].accepted.connect(self.onNewProject)
        self.data.run['w_project_diag_edit'].accepted.connect(self.onEditProject)
        self.widget.push_project_delete.clicked.connect(self.onDeleteProject)

        self.widget.push_project_open.clicked.connect(self.data.load)
        self.widget.push_project_save.clicked.connect(self.data.save)
        
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

        
    def onNewProject(self):

        diag_new = self.data.run['w_project_diag_new']
        
        timestamp = int(time.time())
        pid = self.data.project[0]['next_id']
        project = self.data.project[pid] = {}

        project['category']    = category    = diag_new.combo_category.currentText()
        project['status']      = status      = diag_new.combo_status.currentText()
        project['ptype']       = ptype       = diag_new.combo_ptype.currentText()
        project['basepath']    = basepath    = diag_new.line_basepath.text()
        project['name']        = name        = diag_new.line_name.text()
        project['challenge']   = challenge   = diag_new.spin_challenge.value()
        project['priority']    = priority    = diag_new.spin_priority.value()
        project['description'] = description = diag_new.text_description.toPlainText()
        project['created']     = created     = timestamp

        self.model.insertRow(0, [
            QStandardItem(name),
            QStandardItem(ptype),
            QStandardItem(status),
            QStandardItem(category),
            QStandardItem(str(priority)),
            QStandardItem(str(challenge)),
            QStandardItem('0.0'),
            QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()),
            QStandardItem(str(pid))
        ])

        self.data.project[0]['next_id'] += 1

        self.table.selectRow(0)
        self.table.setFocus()
        self.parent.enableTabs()

        self.widget.push_project_edit.setEnabled(True)
        self.widget.push_project_delete.setEnabled(True)
        self.widget.push_project_details.setEnabled(True)
        self.widget.push_project_save.setEnabled(True)

        self.touchProject(timestamp)
        
    def showEditProject(self):

        pid = self.getSelectedProject()
        self.parent.w_project_diag_edit.line_name.setText(self.data.project[pid]['name'])
        self.parent.w_project_diag_edit.show()

        '''
            lambda: (
            parent.w_project_diag_edit.line_name.setText(self.data.project[self.data.run['sel_project']]['name']), 
            parent.w_project_diag_edit.combo_type.setCurrentIndex(0), 
            parent.w_project_diag_edit.combo_status.setCurrentIndex(0), 
            parent.w_project_diag_edit.combo_category.setCurrentIndex(0), 
            parent.w_project_diag_edit.spin_priority.setValue(0), 
            parent.w_project_diag_edit.spin_challenge.setValue(0), 
            parent.w_project_diag_edit.line_basepath.clear(), 
            parent.w_project_diag_edit.text_description.clear(), 
            parent.w_project_diag_edit.line_name.setFocus(), 
            parent.w_project_diag_edit.show()))

        rd['project']['diag_edit_name'].setText(sd['project']['p'][pid]['name'])
        rd['project']['diag_edit_basepath'].setText(sd['project']['p'][pid]['basepath'])
        self.setComboValue(rd['project']['diag_edit_type'], sd['project']['p'][pid]['type'])
        self.setComboValue(rd['project']['diag_edit_status'], sd['project']['p'][pid]['status'])
        self.setComboValue(rd['project']['diag_edit_category'], sd['project']['p'][pid]['category'])
        rd['project']['diag_edit_priority'].setValue(sd['project']['p'][pid]['priority'])
        rd['project']['diag_edit_challenge'].setValue(sd['project']['p'][pid]['challenge'])
        rd['project']['diag_edit_detail'].setPlainText(sd['project']['p'][pid]['detail'])
        '''

    def onEditProject(self):
        print('project edit submitted')


    def onDeleteProject(self):
        print('deleting project..')


    def touchProject(self, timestamp):

        """
            On project change (e.g. edit meta, add log or change roadmap),
            this should be called with the timestamp. It will update the
            last changed timestamp and update the project index display
            and mark changes as true.
        """
        self.data.project[self.getSelectedProject()]['changed'] = timestamp
        self.model.setItem(self.getActiveRow(), 7, 
            QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()))
        self.data.run['changed'] = True


    def getSelectedProject(self):
        if self.table.currentIndex().row() == -1:
            return 0
        return int(self.model.itemFromIndex(
                self.model.index(self.table.currentIndex().row(), 8)).text())


    def getSelectedProjectName(self):
        return self.model.itemFromIndex(
                self.model(self.table.currentIndex().row(), 0)).text()

    def getActiveRow(self):
        return self.table.currentIndex().row()
        
        """

    ####################   METHODS   #################### 

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
        """

# vim: set ts=4 sw=4 ai si expandtab:

