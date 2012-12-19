#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from pprint import pprint
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton
from milestone import NxMilestone

class NxRoadmap:

    def __init__(self, parent, data, widget):

        # setup backbone
        self.parent = parent
        self.data   = data
        self.widget = widget
        self.mc     = NxMilestone(self.data)
        self.diag_new_edit = self.parent.w_roadmap_diag_add

        # setup table
        self.feature_headers = \
            ['ID', 'Name', 'Type', 'Status', 'Category', 'Priority', 'Created', 'Modified']

        self.model = QStandardItemModel()
        self.table = self.widget.table
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()

        # connect feature / issue add push buttons
        self.widget.push_add_feature.clicked.connect(lambda: (
            self.parent.w_roadmap_diag_add.radio_feature.setChecked(True), self.showAddEditRI('add')))
        self.widget.push_add_issue.clicked.connect(lambda: (
            self.parent.w_roadmap_diag_add.radio_issue.setChecked(True), self.showAddEditRI('add')))
        self.parent.w_roadmap_diag_add.accepted.connect(self.onSubmitDialog)

        # connect all the filter checkboxes to update the milestone item table
        self.widget.check_feature.stateChanged.connect(self.reloadTable)
        self.widget.check_issue.stateChanged.connect(self.reloadTable)
        self.widget.check_open.stateChanged.connect(self.reloadTable)
        self.widget.check_closed.stateChanged.connect(self.reloadTable)
        self.widget.check_low.stateChanged.connect(self.reloadTable)
        self.widget.check_medium.stateChanged.connect(self.reloadTable)
        self.widget.check_high.stateChanged.connect(self.reloadTable)
        self.widget.check_core.stateChanged.connect(self.reloadTable)
        self.widget.check_auxiliary.stateChanged.connect(self.reloadTable)
        self.widget.check_security.stateChanged.connect(self.reloadTable)
        self.widget.check_corrective.stateChanged.connect(self.reloadTable)
        self.widget.check_architecture.stateChanged.connect(self.reloadTable)
        self.widget.check_refactor.stateChanged.connect(self.reloadTable)

        # connect push milestone item action push buttons
        self.widget.push_delete.clicked.connect(self.deleteRoadmapItem)
        self.widget.push_edit.clicked.connect(lambda:(self.showAddEditRI('edit')))
        self.widget.push_close.clicked.connect(self.closeRoadmapItem)

        # connect selection changed (for close item)
        self.selection_model.selectionChanged.connect(
            self.onItemSelectionChanged
        )
        # connect milestone description changed
        self.widget.text_description.textChanged.connect(
            self.onMilestoneDescriptionChanged
        )

    def getCellContent(self, i):

        return int(self.model.itemFromIndex(self.model.index(self.table.currentIndex().row(),i)).text())

    def getSelectedItemId(self):

        return self.getCellContent(0)

    def reloadMilestoneButton(self, targetw='root'):

        cmajor, cminor = self.data.project[self.pid]['meta']['current_milestone']
        milestones = self.data.project[self.pid]['milestone']
        if targetw == 'root':
            self.widget.gridLayout_3.removeWidget(self.widget.push_milestone)
            self.widget.push_milestone.close()
            self.widget.push_milestone = MPushButton(cmajor, cminor, milestones, self.widget, self.onChangeVersionSelection, self.selected_major, self.selected_minor)
            self.widget.gridLayout_3.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
            self.widget.label_2.setBuddy(self.widget.push_milestone)
        elif targetw == 'diag_new_edit':
            self.diag_new_edit.gridLayout_2.removeWidget(self.diag_new_edit.push_target)
            self.diag_new_edit.push_target.close()
            self.diag_new_edit.push_target \
                    = MPushButton(cmajor,cminor,milestones,self.diag_new_edit,None,self.selected_major,self.selected_minor,True)
            self.diag_new_edit.gridLayout_2.addWidget(self.diag_new_edit.push_target, 1, 1, 1, 1);
            self.diag_new_edit.label_3.setBuddy(self.diag_new_edit.push_target)

    def extractSelection(self, targetw='root'):

        if targetw == 'root':
            w = self.widget
            target_label = w.push_target.text()
        elif targetw == 'add_edit_dialog':
            d = self.parent.w_roadmap_diag_add
            target_label = d.push_target.text()

        tmajor, tminor = target_label.split(' ')[3][1:].split('.')
        return int(tmajor), int(tminor)

    def onItemSelectionChanged(self):

        if self.table.currentIndex().row() == -1: return
        status = self.model.itemFromIndex(self.model.index(self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            self.widget.push_close.setText('&Close Item')
        if status == 'Closed':
            self.widget.push_close.setText('Reopen Ite&m')

    def onMilestoneDescriptionChanged(self):

        if self.init: return

        sx, sy = self.mc.versionToIndex(self.selected_major, self.selected_minor)
        self.data.project[self.pid]['milestone'][sx][sy]['description'] = self.widget.text_description.toPlainText()

    def onShowTab(self):

        pid = self.data.run['project'].getSelectedProject()
        if self.data.run['roadmap_pid_last'] == 0 or self.data.run['roadmap_pid_last'] != pid:

            self.pid = pid

            pro = self.data.project[pid]

            project_name = self.data.run['project'].getSelectedProjectName()
            self.widget.line_project.setText(project_name)
            self.parent.w_roadmap_diag_add.line_project.setText(project_name)

            x, y = pro['meta']['current_milestone']
            milestones = pro['milestone']

            self.widget.gridLayout_3.removeWidget(self.widget.push_milestone)
            self.widget.push_milestone.close()
            self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection)
            self.widget.gridLayout_3.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
            self.widget.label_2.setBuddy(self.widget.push_milestone)

            self.reloadTable()

            # computing next_x, next_y is quite tricky, so we take it from the milestone widget (which does it anyway)
            self.selected_major = self.widget.push_milestone.next_x
            self.selected_minor = self.widget.push_milestone.next_y

            d = self.parent.w_roadmap_diag_add
            d.radio_medium.setChecked(True)
            d.radio_feature.setChecked(True)

    def closeRoadmapItem(self):

        if self.table.currentIndex().row() == -1: return
        status = self.model.itemFromIndex(self.model.index(self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            self.mc.closeItem(self.pid, self.getSelectedItemId())
        if status == 'Closed':
            self.mc.reopenItem(self.pid, self.getSelectedItemId())
        self.data.run['project'].touchProject(time.time())
        self.reloadTable()

    def onChangeVersionSelection(self, major, minor, current_text):

        self.selected_major = major
        self.selected_minor = minor
        sx, sy = self.mc.versionToIndex(major, minor)
        self.widget.text_description.setPlainText(
            self.data.project[self.pid]['milestone'][sx][sy]['description']
        )

        self.reloadTable()

    def prependTable(self, key, itype, status, priority, icat, v):

        if itype == 'Feature' and not self.widget.check_feature.isChecked(): return
        if itype == 'Issue' and not self.widget.check_issue.isChecked(): return
        if status == 'Open' and not self.widget.check_open.isChecked(): return
        if status == 'Closed' and not self.widget.check_closed.isChecked(): return
        if priority == 'Low' and not self.widget.check_low.isChecked(): return
        if priority == 'Medium' and not self.widget.check_medium.isChecked(): return
        if priority == 'High' and not self.widget.check_high.isChecked(): return
        if icat == 'Core' and not self.widget.check_core.isChecked(): return
        if icat == 'Auxiliary' and not self.widget.check_auxiliary.isChecked(): return
        if icat == 'Security' and not self.widget.check_security.isChecked(): return
        if icat == 'Correction' and not self.widget.check_corrective.isChecked(): return
        if icat == 'Architecture' and not self.widget.check_architecture.isChecked(): return
        if icat == 'Refactor' and not self.widget.check_refactor.isChecked(): return

        self.model.insertRow(0, [
            QStandardItem(str(key)),
            QStandardItem(v['name']),
            QStandardItem(itype),
            QStandardItem(status),
            QStandardItem(icat),
            QStandardItem(str(v['priority'])),
            QStandardItem(datetime.datetime.fromtimestamp(v['created']).isoformat()),
            QStandardItem(datetime.datetime.fromtimestamp(v['modified']).isoformat())
        ])

    def reloadTable(self):

        self.selected_major, self.selected_minor = self.widget.push_milestone.getVersion()

        self.init = True
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        self.widget.push_close.setText('&Close Item')

        pid = self.data.run['project'].getSelectedProject()
        cmajor, cminor = self.data.project[pid]['meta']['current_milestone']
        yy = self.selected_minor
        if self.selected_major == 0: yy = self.selected_minor-1
        fo = self.data.project[pid]['milestone'][self.selected_major][yy]['fo']
        fc = self.data.project[pid]['milestone'][self.selected_major][yy]['fc']
        io = self.data.project[pid]['milestone'][self.selected_major][yy]['io']
        ic = self.data.project[pid]['milestone'][self.selected_major][yy]['ic']

        for key, value in ic.items():
            itype = 'Issue'
            status = 'Closed'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in fc.items():
            itype = 'Feature'
            status = 'Closed'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in io.items():
            itype = 'Issue'
            status = 'Open'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in fo.items():
            itype = 'Feature'
            status = 'Open'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)

        self.init = False

        # only enable controls for future milestones
        if self.model.rowCount() > 0:
            if self.selected_major > cmajor or (self.selected_major == cmajor and self.selected_minor > cminor):
                self.widget.push_edit.setEnabled(True)
                self.widget.push_delete.setEnabled(True)
                self.widget.push_close.setEnabled(True)
            else:
                self.widget.push_edit.setEnabled(False)
                self.widget.push_delete.setEnabled(False)
                self.widget.push_close.setEnabled(False)
            self.table.selectRow(0)

        self.table.setFocus()

    def showAddEditRI(self, diag_type=None):

        self.reloadMilestoneButton('diag_new_edit')

        # set dialog type flag
        if diag_type == 'add':
            self.diag_type = 'add'
            self.diag_new_edit.setWindowTitle('Add Roadmap Item')
            self.diag_new_edit.line_name.clear()
            self.diag_new_edit.text_description.clear()
        else:
            self.diag_type = 'edit'
            self.diag_new_edit.setWindowTitle('Edit Roadmap Item')

            item_id = self.getSelectedItemId()
            tmajor, tminor, fioc = self.data.project[self.pid]['ri_index'][item_id]
            tx, ty = self.mc.versionToIndex(tmajor, tminor)
            item = self.data.project[self.pid]['milestone'][tx][ty][fioc][item_id]

            if fioc[0] == 'f': itype = 'Feature'
            if fioc[0] == 'i': itype = 'Isssue'

            if itype == 'Feature': self.diag_new_edit.radio_feature.setChecked(True)
            if itype == 'Issue': self.diag_new_edit.radio_issue.setChecked(True)
            if item['priority'] == 'Low': self.diag_new_edit.radio_low.setChecked(True)
            if item['priority'] == 'Medium': self.diag_new_edit.radio_medium.setChecked(True)
            if item['priority'] == 'High': self.diag_new_edit.radio_high.setChecked(True)
            if item['icat'] == 'Core': self.diag_new_edit.radio_core.setChecked(True)
            if item['icat'] == 'Auxiliary': self.diag_new_edit.radio_auxiliary.setChecked(True)
            if item['icat'] == 'Security': self.diag_new_edit.radio_security.setChecked(True)
            if item['icat'] == 'Correction': self.diag_new_edit.radio_corrective.setChecked(True)
            if item['icat'] == 'Architecture': self.diag_new_edit.radio_architecture.setChecked(True)
            if item['icat'] == 'Refactor': self.diag_new_edit.radio_refactor.setChecked(True)

        # show dialog
        self.diag_new_edit.show()
        self.diag_new_edit.line_name.setFocus()

    def onSubmitDialog(self):

        # simple switch between add and edit mode for the dialog
        if self.diag_type == 'add':
            self.onSubmitNewEditRI('add')
        if self.diag_type == 'edit':
            self.onSubmitNewEditRI('edit')

    def onSubmitNewEditRI(self, mode):

        pid = self.data.run['project'].getSelectedProject()
        tmajor, tminor = self.extractSelection('add_edit_dialog')

        name = self.diag_new_edit.line_name.text()
        description = self.diag_new_edit.text_description.toPlainText()

        if self.diag_new_edit.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'

        if self.diag_new_edit.radio_medium.isChecked():
            priority = 'Medium'
        elif self.diag_new_edit.radio_high.isChecked():
            priority = 'High'
        elif self.diag_new_edit.radio_low.isChecked():
            priority = 'Low'

        if self.diag_new_edit.radio_core.isChecked():
            category = 'Core'
        elif self.diag_new_edit.radio_auxiliary.isChecked():
            category = 'Auxiliary'
        elif self.diag_new_edit.radio_security.isChecked():
            category = 'Security'
        elif self.diag_new_edit.radio_corrective.isChecked():
            category = 'Corrective'
        elif self.diag_new_edit.radio_architecture.isChecked():
            category = 'Architecture'
        elif self.diag_new_edit.radio_refactor.isChecked():
            category = 'Refactor'

        if mode == 'add':
            self.mc.addItem(
                pid, tmajor, tminor, ri_type, category, name, priority, description
            )
        if mode == 'edit':
            self.mc.editItem(
                pid, tmajor, tminor, self.getSelectedItemId(), ri_type, category, name, priority, description
            )

        self.reloadMilestoneButton()
        self.reloadTable()

        self.data.run['project'].touchProject(int(time.time()))

    def deleteRoadmapItem(self):

        xid = self.getSelectedItemId()
        pid = self.data.run['project'].getSelectedProject()
        p = self.data.project[pid]
        tx, ty, fioc = p['ri_index'][xid]
        del p['milestone'][tx][ty][fioc][xid]
        del p['ri_index'][xid]
        self.model.removeRow(self.table.currentIndex().row())
        timestamp = int(time.time())
        self.data.run['project'].touchProject(timestamp)
        if self.model.rowCount() == 0:
            self.widget.push_edit.setEnabled(False)
            self.widget.push_delete.setEnabled(False)
            self.widget.push_close.setEnabled(False)

