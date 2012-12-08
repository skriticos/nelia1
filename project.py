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

        self.widget.push_project_open.clicked.connect(lambda: (self.data.load() and self.reset()))
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

        timestamp = int(time.time())
        pid = self.data.project[0]['next_id']
        # meta: general project data
        # log: log data
        # milestone: versions, features, issues
        p = self.data.project[pid] = {  'meta': {'last_log': 0, 'last_feature': 0, 'last_issue': 0, 'current_milestone': (0,0)},
                                        'log': {},
                                        'milestone' : [
                                                [{'m': '0.1', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}],
                                                [{'m': '1.0', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
                                            ]}
        d = self.data.run['w_project_diag_new']

        p['name']        = name        = d.line_name.text()
        p['category']    = category    = d.combo_category.currentText()
        p['status']      = status      = d.combo_status.currentText()
        p['ptype']       = ptype       = d.combo_ptype.currentText()
        p['priority']    = priority    = d.spin_priority.value()
        p['challenge']   = challenge   = d.spin_challenge.value()
        p['basepath']    = basepath    = d.line_basepath.text()
        p['description'] = description = d.text_description.toPlainText()
        p['created']     = created     = timestamp

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
        p = self.data.project[pid]
        d = self.parent.w_project_diag_edit

        d.line_name.setText(p['name'])
        d.combo_ptype.setCurrentIndex(d.combo_ptype.findText(p['ptype']))
        d.combo_status.setCurrentIndex(d.combo_status.findText(p['status']))
        d.combo_category.setCurrentIndex(d.combo_category.findText(p['category']))
        d.spin_priority.setValue(p['priority'])
        d.spin_challenge.setValue(p['challenge'])
        d.line_basepath.setText(p['basepath'])
        d.text_description.setPlainText(p['description'])

        d.show()
        d.line_name.setFocus()

    def onEditProject(self):

        pid = self.getSelectedProject()
        p = self.data.project[pid]
        d = self.parent.w_project_diag_edit
        timestamp = int(time.time())
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        p['name']        = name        = d.line_name.text()
        p['category']    = category    = d.combo_category.currentText()
        p['status']      = status      = d.combo_status.currentText()
        p['ptype']       = ptype       = d.combo_ptype.currentText()
        p['priority']    = priority    = d.spin_priority.value()
        p['challenge']   = challenge   = d.spin_challenge.value()
        p['basepath']    = basepath    = d.line_basepath.text()
        p['description'] = description = d.text_description.toPlainText()

        for index, value in (
                            (0, name),
                            (1, ptype),
                            (2, status),
                            (3, category),
                            (4, priority),
                            (5, challenge),
                            (6, '0.0'), # FIXME: fetch this from milestones
                            (7, disptime),
                            (8, str(pid))):
            self.model.setData(
                self.model.index(self.getActiveRow(), index), value)

        self.touchProject(timestamp)

    def onDeleteProject(self):

        pid = self.getSelectedProject()

        response = QMessageBox.question(
            self.widget,
            'Delete project?',
            'Sure you want to delete project {}: {}?'.format(str(pid), self.getSelectedProjectName()),
            QMessageBox.Yes|QMessageBox.No)

        if response == QMessageBox.StandardButton.No:
            return

        del self.data.project[pid]
        self.model.removeRow(self.getActiveRow())

        if self.model.rowCount() == 0:
            self.parent.dissableTabs()
        else:
            self.table.selectRow(0)

        # can't touch deleted project, direct changed update
        self.data.run['changed'] = True

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
                self.model.index(self.table.currentIndex().row(), 0)).text()

    def getActiveRow(self):
        return self.table.currentIndex().row()

    def reset(self):

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.table_headers)

        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(4, 50)
        self.table.setColumnWidth(5, 50)
        self.table.setColumnWidth(6, 80)
        self.table.setColumnWidth(7, 160)
        self.table.setColumnWidth(8, 80)

        for pid,project in self.data.project.items():
            if pid == 0: continue
            disptime = datetime.datetime.fromtimestamp(project['changed']).isoformat()
            self.model.insertRow(0, [
                QStandardItem(project['name']),
                QStandardItem(project['ptype']),
                QStandardItem(project['status']),
                QStandardItem(project['category']),
                QStandardItem(str(project['priority'])),
                QStandardItem(str(project['challenge'])),
                QStandardItem('0.0'), # FIXME: get this from milestones
                QStandardItem(disptime),
                QStandardItem(str(pid))
            ])

        self.table.selectRow(0)
        self.table.setFocus()

        self.parent.enableTabs()
        self.widget.push_project_edit.setEnabled(True)
        self.widget.push_project_delete.setEnabled(True)
        self.widget.push_project_details.setEnabled(True)
        self.widget.push_project_save.setEnabled(True)

        self.data.run['changed'] = False

# vim: set ts=4 sw=4 ai si expandtab:

