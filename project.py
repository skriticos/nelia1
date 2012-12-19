#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import os, datetime, time

class NxProject:

    def __init__(self, parent, datastore, widget):

        # setup backbone
        self.parent = parent
        self.data   = datastore
        self.widget = widget

        # show new project dialog
        self.widget.push_new.clicked.connect(
            lambda: (
            parent.w_project_diag_new.line_name.clear(),
            parent.w_project_diag_new.combo_ptype.setCurrentIndex(0),
            parent.w_project_diag_new.combo_status.setCurrentIndex(0),
            parent.w_project_diag_new.combo_category.setCurrentIndex(0),
            parent.w_project_diag_new.spin_priority.setValue(0),
            parent.w_project_diag_new.spin_challenge.setValue(0),
            parent.w_project_diag_new.text_description.clear(),
            parent.w_project_diag_new.line_name.setFocus(),
            parent.w_project_diag_new.show()))

        # show edit project dialog
        self.widget.push_edit.clicked.connect(self.showEditProject)

        self.data.run['w_project_diag_new'].accepted.connect(self.onNewProject)
        self.data.run['w_project_diag_edit'].accepted.connect(self.onEditProject)
        self.widget.push_delete.clicked.connect(self.onDeleteProject)

        self.widget.push_open.clicked.connect(lambda: (
            self.data.load(),
            self.reset()
        ))
        self.widget.push_save.clicked.connect(self.data.save)

        self.widget.push_help.clicked.connect(self.parent.w_project_diag_help.show)

        # setup table
        self.table = self.widget.table_project_list
        self.table_headers = [
                'ID', 'Name', 'Status', 'Type', 'Verson', 'Category', 'Priority', 'Challenge',
                'Modified', 'Created'
                ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()

        self.diag_new = self.parent.w_project_diag_new
        self.diag_edit = self.parent.w_project_diag_edit

        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        self.widget.text_description.textChanged.connect(self.onDescriptionChange)

        self.table.activated.connect(self.showEditProject)

    def touchProject(self, timestamp):

        """
            On project change (e.g. edit meta, add log or change roadmap),
            this should be called with the timestamp. It will update the
            last changed timestamp and update the project index display
            and mark changes as true.
        """
        self.data.project[self.getSelectedProject()]['modified'] = timestamp
        self.model.setItem(self.getActiveRow(), 8,
            QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()))
        self.data.run['changed'] = True

    def getSelectedProject(self):
        if not self.init:
            if self.table.currentIndex().row() == -1:
                return 0
            return int(self.model.itemFromIndex(
                    self.model.index(self.table.currentIndex().row(), 0)).text())


    def getSelectedProjectName(self):
        return self.model.itemFromIndex(
                self.model.index(self.table.currentIndex().row(), 1)).text()

    def getActiveRow(self):
        return self.table.currentIndex().row()

    def onSelectionChanged(self):

        if not self.init:
            pid = self.getSelectedProject()
            if self.data.project[0]['next_id'] > 1 and pid != 0:
                self.widget.text_description.setEnabled(True)
                self.widget.text_description.setPlainText(
                    self.data.project[pid]['description']
                )

    def onDescriptionChange(self):

        self.data.project[self.getSelectedProject()]['description'] = \
                self.widget.text_description.toPlainText()

    def reloadTable(self):

        self.init = True
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.table_headers)

        for pid, project in self.data.project.items():
            if pid == 0: continue
            major, minor = self.data.project[pid]['meta']['current_milestone']
            disptime1 = datetime.datetime.fromtimestamp(project['modified']).isoformat()
            disptime2 = datetime.datetime.fromtimestamp(project['created']).isoformat()
            self.model.insertRow(0, [
                QStandardItem(str(pid)),
                QStandardItem(project['name']),
                QStandardItem(project['status']),
                QStandardItem(project['ptype']),
                QStandardItem('{}.{}'.format(major,minor)),
                QStandardItem(project['category']),
                QStandardItem(str(project['priority'])),
                QStandardItem(str(project['challenge'])),
                QStandardItem(disptime1),
                QStandardItem(disptime2),
            ])

        self.table.sortByColumn(0, Qt.DescendingOrder)

        self.init = False

        if len(self.data.project) > 1:

            self.table.selectRow(0)

            self.parent.enableTabs()
            self.widget.push_edit.setEnabled(True)
            self.widget.push_delete.setEnabled(True)
            self.widget.push_save.setEnabled(True)

            self.table.setFocus()

        else:

            self.widget.text_description.clear()
            self.widget.text_description.setEnabled(False)
            self.parent.dissableTabs()
            self.widget.push_edit.setEnabled(False)
            self.widget.push_delete.setEnabled(False)
            self.widget.push_save.setEnabled(False)
            self.widget.push_new.setFocus()

    def onNewProject(self):

        timestamp = int(time.time())
        pid = self.data.project[0]['next_id']

        # create new project entry
        # meta: general project data
        # log: log data
        # milestone: versions, features, issues
        p = self.data.project[pid] = {  'meta': {'last_log': 0, 'last_roadmap_item': 0, 'current_milestone': (0,0)},
                                        'log': {},
                                        'milestone' : [
                                            [{'description': '', 'm': '0.1', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}],
                                            [{'description': '', 'm': '1.0', 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
                                            ],
                                        'ri_index' : {}
                                     }

        p['name']        = name        = self.diag_new.line_name.text()
        p['category']    = category    = self.diag_new.combo_category.currentText()
        p['status']      = status      = self.diag_new.combo_status.currentText()
        p['ptype']       = ptype       = self.diag_new.combo_ptype.currentText()
        p['priority']    = priority    = self.diag_new.spin_priority.value()
        p['challenge']   = challenge   = self.diag_new.spin_challenge.value()
        p['description'] = description = self.diag_new.text_description.toPlainText()
        p['created']     = created     = timestamp
        p['modified']    = timestamp

        self.data.project[0]['next_id'] += 1

        self.reloadTable()
        self.touchProject(timestamp)

    def showEditProject(self):

        p = self.data.project[self.getSelectedProject()]

        self.diag_edit.line_name.setText(p['name'])
        self.diag_edit.combo_ptype.setCurrentIndex(self.diag_edit.combo_ptype.findText(p['ptype']))
        self.diag_edit.combo_status.setCurrentIndex(self.diag_edit.combo_status.findText(p['status']))
        self.diag_edit.combo_category.setCurrentIndex(self.diag_edit.combo_category.findText(p['category']))
        self.diag_edit.spin_priority.setValue(p['priority'])
        self.diag_edit.spin_challenge.setValue(p['challenge'])
        self.diag_edit.text_description.setPlainText(p['description'])

        self.diag_edit.show()
        self.diag_edit.line_name.setFocus()

    def onEditProject(self):

        pid = self.getSelectedProject()
        p = self.data.project[pid]
        timestamp = int(time.time())
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        p['name']        = self.diag_edit.line_name.text()
        p['category']    = self.diag_edit.combo_category.currentText()
        p['status']      = self.diag_edit.combo_status.currentText()
        p['ptype']       = self.diag_edit.combo_ptype.currentText()
        p['priority']    = self.diag_edit.spin_priority.value()
        p['challenge']   = self.diag_edit.spin_challenge.value()
        p['description'] = self.diag_edit.text_description.toPlainText()

        self.reloadTable()
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
        self.reloadTable()

        # can't touch deleted project, direct changed update
        self.data.run['changed'] = True

    def reset(self):

        self.reloadTable()
        self.data.run['changed'] = False

# vim: set ts=4 sw=4 ai si expandtab:

