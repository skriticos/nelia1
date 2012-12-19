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
        self.widget.push_edit.clicked.connect(self.editRoadmapItem)
        self.widget.push_close.clicked.connect(self.closeRoadmapItem)

        # connect selection changed (for close item)
        self.selection_model.selectionChanged.connect(
            self.onItemSelectionChanged
        )

    def getCellContent(self, i):

        return int(self.model.itemFromIndex(self.model.index(self.table.currentIndex().row(),i)).text())

    def getSelectedItemId(self):

        return self.getCellContent(0)

    def reloadMilestoneButton(self, targetw='root', tmajor=None, tminor=None):

        x, y = self.data.project[self.pid]['meta']['current_milestone']
        milestones = self.data.project[self.pid]['milestone']
        self.widget.gridLayout_3.removeWidget(self.widget.push_milestone)
        self.widget.push_milestone.close()
        self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection, self.selected_x, self.selected_y)
        self.widget.gridLayout_3.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
        self.widget.label_2.setBuddy(self.widget.push_milestone)

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
            self.widget.push_close.setEnabled(True)
        if status == 'Closed':
            self.widget.push_close.setEnabled(False)

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
            self.selected_x = self.widget.push_milestone.next_x
            self.selected_y = self.widget.push_milestone.next_y

            d = self.parent.w_roadmap_diag_add
            d.radio_medium.setChecked(True)
            d.radio_feature.setChecked(True)

    def closeRoadmapItem(self):

        self.mc.closeItem(self.pid, self.getSelectedItemId())
        self.data.run['project'].touchProject(time.time())
        self.reloadTable()

    def onChangeVersionSelection(self, x, y, current_text):

        self.selected_x = x
        self.selected_y = y

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

        self.selected_x, self.selected_y = self.widget.push_milestone.getVersion()

        self.init = True
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.feature_headers)

        pid = self.data.run['project'].getSelectedProject()
        cmajor, cminor = self.data.project[pid]['meta']['current_milestone']
        yy = self.selected_y
        if self.selected_x == 0: yy = self.selected_y-1
        fo = self.data.project[pid]['milestone'][self.selected_x][yy]['fo']
        fc = self.data.project[pid]['milestone'][self.selected_x][yy]['fc']
        io = self.data.project[pid]['milestone'][self.selected_x][yy]['io']
        ic = self.data.project[pid]['milestone'][self.selected_x][yy]['ic']

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

        if self.model.rowCount() > 0:
            self.table.selectRow(0)
            self.widget.push_edit.setEnabled(True)
            self.widget.push_delete.setEnabled(True)
            self.widget.push_close.setEnabled(True)

        self.table.setFocus()

    def showAddEditRI(self, diag_type=None):

        # initialize variables
        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        cx, cy = self.data.project[pid]['meta']['current_milestone']
        d = self.parent.w_roadmap_diag_add

        # reload milestone push button on dialog (to match parent selection)
        d.gridLayout_2.removeWidget(d.push_target)
        d.push_target.close()
        d.push_target \
                = MPushButton(cx,cy,milestones,d,None,self.selected_x,self.selected_y,True)
        d.gridLayout_2.addWidget(d.push_target, 1, 1, 1, 1);
        d.label_3.setBuddy(d.push_target)

        # set dialog type flag
        if diag_type == 'add':
            self.diag_type = 'add'
        else:
            self.diag_type = 'edit'

        # reset dialog controls and title
        d.line_name.clear()
        d.text_description.clear()
        d.setWindowTitle('Add Roadmap Item')

        # show dialog
        d.show()
        d.line_name.setFocus()

    def onSubmitDialog(self):

        # simple switch between add and edit mode for the dialog
        if self.diag_type == 'add':
            self.onSubmitNewRoadmapItem()
        if self.diag_type == 'edit':
            self.onSubmitEditRoadmapItem()

    def onSubmitNewRoadmapItem(self):

        pid = self.data.run['project'].getSelectedProject()
        d = self.parent.w_roadmap_diag_add
        tmajor, tminor = self.extractSelection('add_edit_dialog')

        name = d.line_name.text()
        description = d.text_description.toPlainText()

        if d.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'

        if d.radio_medium.isChecked():
            priority = 'Medium'
        elif d.radio_high.isChecked():
            priority = 'High'
        elif d.radio_low.isChecked():
            priority = 'Low'

        if d.radio_core.isChecked():
            category = 'Core'
        elif d.radio_auxiliary.isChecked():
            category = 'Auxiliary'
        elif d.radio_security.isChecked():
            category = 'Security'
        elif d.radio_corrective.isChecked():
            category = 'Corrective'
        elif d.radio_architecture.isChecked():
            category = 'Architecture'
        elif d.radio_refactor.isChecked():
            category = 'Refactor'

        self.mc.addItem(
            pid, tmajor, tminor, ri_type, category, name, priority, description
        )

        self.reloadMilestoneButton()
        self.reloadTable()

        self.data.run['project'].touchProject(int(time.time()))

    def editRoadmapItem(self):

        xid = self.getSelectedItemId()
        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        p = self.data.project[pid]
        tx, ty, fioc = p['ri_index'][xid]
        item = p['milestone'][tx][ty][fioc][xid]
        d = self.parent.w_roadmap_diag_add
        d.setWindowTitle('Edit Roadmap Item')
        x, y = self.data.project[pid]['meta']['current_milestone']

        self.diag_type = 'edit'

        # can't edit what you don't see (edit is always in the current selected milestone)
        d.gridLayout_2.removeWidget(d.push_target)
        d.push_target.close()
        d.push_target \
                = MPushButton(x,y,milestones,d,None,self.selected_x,self.selected_y,True)
        d.gridLayout_2.addWidget(d.push_target, 1, 1, 1, 1);
        d.label_3.setBuddy(d.push_target)

        if ty == 0: ty += 1

        d.line_name.setText(item['name'])
        if item['ri_type'] == 'Feature':
            d.radio_feature.setChecked(True)
        else:
            d.radio_issue.setChecked(True)

        if d.radio_medium.isChecked():
            prio = 'Medium'
        elif d.radio_high.isChecked():
            prio = 'High'
        else:
            prio = 'Low'

        if item['priority'] == 'Medium':
            d.radio_medium.setChecked(True)
        elif item['priority'] == 'High':
            d.radio_high.setChecked(True)
        elif item['priority'] == 'Low':
            d.radio_low.setChecked(True)

        d.show()
        d.line_name.setFocus()

    def onSubmitEditRoadmapItem(self):


        # TODO: on move item during edit -> move milestone

        pid = self.data.run['project'].getSelectedProject()
        xid = item_id = self.getSelectedItemId()
        milestones = self.data.project[pid]['milestone']
        d = self.parent.w_roadmap_diag_add
        target_label = d.push_target.text()
        timestamp = int(time.time())
        p = self.data.project[pid]
        tx, ty, fioc = p['ri_index'][xid]
        item = p['milestone'][tx][ty][fioc][xid]
        tx2, ty2 = target_label.split(' ')[3][1:].split('.')
        tx2 = int(tx)
        ty2 = int(ty)

        item['name'] = d.line_name.text()
        description = d.text_description.toPlainText()
        if d.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'
        if d.radio_medium.isChecked():
            prio = 'Medium'
        elif d.radio_high.isChecked():
            prio = 'High'
        elif d.radio_low.isChecked():
            prio = 'Low'

        item['ri_type'] = ri_type
        item['priority'] = prio
        item['description'] = description

        if (tx, ty) != (tx2, ty2):

            del p['milestone'][tx][ty][fioc]

            # generate new milestones if an edge is reached
            a = {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
            b = {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
            if len(milestones) > tx2 + 1:
                if (tx2 != 0 and len(milestones[tx2]) == ty2 + 1) or (tx2 == 0 and len(milestones[tx2]) == ty2):
                    a['m'] = '{}.{}'.format(tx2, ty2)
                    milestones[tx2].append(a)
            else:
                a['m'] = '{}.{}'.format(tx2, 1)
                milestones[tx2].append(a)
                b['m'] = '{}.{}'.format(tx2+1, 0)
                milestones.append([b])

            # update push button
            if tx2 == 0:
                ty2 -= 1

            if ri_ty2pe == 'Feature':
                self.data.project[pid]['milestone'][tx2][ty2]['fo'][item_id] = new_item
                p['ri_index'][item_id] = (tx2, ty2, 'fo')
            else:
                self.data.project[pid]['milestone'][tx2][ty2]['io'][item_id] = new_item
                p['ri_index'][item_id] = (tx2, ty2, 'io')

        self.reloadTable()
        self.data.run['project'].touchProject(timestamp)

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

# vim: set ts=4 sw=4 ai si expandtab:

