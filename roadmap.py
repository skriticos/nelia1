#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from pprint import pprint
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton

class NxRoadmap(QObject):

    def __init__(self, parent, datastore, widget):

        self.parent = parent
        self.data   = datastore
        self.widget = widget

        self.milestone_menu = QMenu(self.widget)
        self.widget.push_milestone.setMenu(self.milestone_menu)

        self.feature_headers = \
            ['Name', 'Type', 'Target', 'Priority', 'Status', 'Created', 'ID']

        self.model = QStandardItemModel()
        self.table = self.widget.table
        self.table.setModel(self.model)

        self.widget.push_add_feature.clicked.connect(lambda: (self.parent.w_roadmap_diag_add.radio_feature.setChecked(True), self.showAddRoadmapItem()))
        self.widget.push_add_issue.clicked.connect(lambda: (self.parent.w_roadmap_diag_add.radio_issue.setChecked(True), self.showAddRoadmapItem()))
        self.parent.w_roadmap_diag_add.accepted.connect(self.onSubmitNewRoadmapItem)

    def onShowTab(self):

        pid = self.data.run['project'].getSelectedProject()
        if self.data.run['roadmap_pid_last'] == 0 or self.data.run['roadmap_pid_last'] != pid:

            pro = self.data.project[pid]

            project_name = self.data.run['project'].getSelectedProjectName()
            self.widget.line_project.setText(project_name)
            self.parent.w_roadmap_diag_add.line_project.setText(project_name)

            x, y = pro['meta']['current_milestone']
            milestones = pro['milestone']

            self.widget.gridLayout_2.removeWidget(self.widget.push_milestone)
            self.widget.push_milestone.close()
            self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection)
            self.widget.gridLayout_2.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
            self.widget.label_2.setBuddy(self.widget.push_milestone)

            self.reloadTables()

            # computing next_x, next_y is quite tricky, so we take it from the milestone widget (which does it anyway)
            self.selected_x = self.widget.push_milestone.next_x
            self.selected_y = self.widget.push_milestone.next_y

            d = self.parent.w_roadmap_diag_add
            d.radio_medium.setChecked(True)
            d.radio_feature.setChecked(True)

            self.widget.check_feature.stateChanged.connect(self.reloadTables)
            self.widget.check_issue.stateChanged.connect(self.reloadTables)
            self.widget.check_open.stateChanged.connect(self.reloadTables)
            self.widget.check_closed.stateChanged.connect(self.reloadTables)

    def onChangeVersionSelection(self, x, y, current_text):

        self.selected_x = x
        self.selected_y = y

        self.reloadTables()

    def reloadTables(self):

        self.selected_x, self.selected_y = self.widget.push_milestone.getVersion()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        self.table.setColumnWidth(0, 450)
        self.table.setColumnWidth(1, 80)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 160)
        self.table.setColumnWidth(6, 80)

        pid = self.data.run['project'].getSelectedProject()
        pro = self.data.project[pid]
        x, y = pro['meta']['current_milestone']
        yy = self.selected_y
        if self.selected_x == 0: yy = self.selected_y-1
        fo = pro['milestone'][self.selected_x][yy]['fo']
        fc = pro['milestone'][self.selected_x][yy]['fc']
        io = pro['milestone'][self.selected_x][yy]['io']
        ic = pro['milestone'][self.selected_x][yy]['ic']

        if self.widget.check_feature.isChecked():
            if self.widget.check_closed.isChecked():
                for key, value in fc.items():
                    self.model.insertRow(0, [
                        QStandardItem(value['name']),
                        QStandardItem(value['ri_type']),
                        QStandardItem('{}.{}'.format(self.selected_x, self.selected_y)),
                        QStandardItem(value['priority']),
                        QStandardItem('Closed'),
                        QStandardItem(datetime.datetime.fromtimestamp(value['created']).isoformat()),
                        QStandardItem(str(key))
                    ])
                    self.table.selectRow(0)
            if self.widget.check_open.isChecked():
                for key, value in fo.items():
                    self.model.insertRow(0, [
                        QStandardItem(value['name']),
                        QStandardItem(value['ri_type']),
                        QStandardItem('{}.{}'.format(self.selected_x, self.selected_y)),
                        QStandardItem(value['priority']),
                        QStandardItem('Open'),
                        QStandardItem(datetime.datetime.fromtimestamp(value['created']).isoformat()),
                        QStandardItem(str(key))
                    ])
                    self.table.selectRow(0)
        if self.widget.check_issue.isChecked():
            if self.widget.check_closed.isChecked():
                for key, value in ic.items():
                    self.model.insertRow(0, [
                        QStandardItem(value['name']),
                        QStandardItem(value['ri_type']),
                        QStandardItem('{}.{}'.format(self.selected_x, self.selected_y)),
                        QStandardItem(value['priority']),
                        QStandardItem('Closed'),
                        QStandardItem(datetime.datetime.fromtimestamp(value['created']).isoformat()),
                        QStandardItem(str(key))
                    ])
                    self.table.selectRow(0)
            if self.widget.check_open.isChecked():
                for key, value in io.items():
                    self.model.insertRow(0, [
                        QStandardItem(value['name']),
                        QStandardItem(value['ri_type']),
                        QStandardItem('{}.{}'.format(self.selected_x, self.selected_y)),
                        QStandardItem(value['priority']),
                        QStandardItem('Open'),
                        QStandardItem(datetime.datetime.fromtimestamp(value['created']).isoformat()),
                        QStandardItem(str(key))
                    ])
                    self.table.selectRow(0)
        self.table.setFocus()
        if self.table.currentIndex().row() == 0:
            self.widget.push_edit.setEnabled(True)
            self.widget.push_delete.setEnabled(True)

    def showAddRoadmapItem(self):

        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        x, y = self.data.project[pid]['meta']['current_milestone']
        d = self.parent.w_roadmap_diag_add

        d.gridLayout_2.removeWidget(d.push_target)
        d.push_target.close()
        d.push_target \
                = MPushButton(x,y,milestones,d,None,self.selected_x,self.selected_y,True)
        d.gridLayout_2.addWidget(d.push_target, 1, 1, 1, 1);

        d.line_name.clear()
        d.text_description.clear()
        d.show()
        d.line_name.setFocus()

    def onSubmitNewRoadmapItem(self):

        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        d = self.parent.w_roadmap_diag_add
        x, y = self.data.project[pid]['meta']['current_milestone']
        target_label = d.push_target.text()
        tx, ty = target_label.split(' ')[3][1:].split('.')
        tx = int(tx)
        ty = int(ty)
        timestamp = int(time.time())

        name = d.line_name.text()
        description = d.text_description.toPlainText()
        if d.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'
        if d.radio_medium.isChecked():
            prio = 'Medium'
        elif d.radio_high.isChecked():
            prio = 'High'
        else:
            prio = 'Low'

        new_item = {
            'name':         name,
            'ri_type':      ri_type,
            'priority':     prio,
            'description':  description,
            'created':      timestamp,
            'closed':       False
        }

        # only add feature, if added to currently selected version
        if tx == self.selected_x and ty == self.selected_y:
            # add to feature table
            model = self.model
            model.insertRow(0, [
                QStandardItem(name),
                QStandardItem(ri_type),
                QStandardItem('{}.{}'.format(tx,ty)),
                QStandardItem(prio),
                QStandardItem('Open'),
                QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()),
                QStandardItem(str(self.data.project[pid]['meta']['last_roadmap_item']+1))
            ])

        # generate new milestones if an edge is reached
        a = {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
        b = {'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
        if len(milestones) > tx + 1:
            if (tx != 0 and len(milestones[tx]) == ty + 1) or (tx == 0 and len(milestones[tx]) == ty):
                a['m'] = '{}.{}'.format(tx, ty)
                milestones[tx].append(a)
        else:
            a['m'] = '{}.{}'.format(tx, 1)
            milestones[tx].append(a)
            b['m'] = '{}.{}'.format(tx+1, 0)
            milestones.append([b])

        # update push button
        if tx == 0:
            ty -= 1

        if ri_type == 'Feature':
            self.data.project[pid]['milestone'][tx][ty]['fo'][self.data.project[pid]['meta']['last_roadmap_item']+1] = new_item
        else:
            self.data.project[pid]['milestone'][tx][ty]['io'][self.data.project[pid]['meta']['last_roadmap_item']+1] = new_item
        self.data.project[pid]['meta']['last_roadmap_item'] += 1

        self.widget.gridLayout_2.removeWidget(self.widget.push_milestone)
        self.widget.push_milestone.close()
        self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection, self.selected_x, self.selected_y)
        self.widget.gridLayout_2.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
        self.widget.label_2.setBuddy(self.widget.push_milestone)

        self.table.selectRow(0)
        self.table.setFocus()
        if self.table.currentIndex().row() == 0:
            self.widget.push_edit.setEnabled(True)
            self.widget.push_delete.setEnabled(True)
            self.widget.push_close.setEnabled(True)

        self.data.run['project'].touchProject(timestamp)

# vim: set ts=4 sw=4 ai si expandtab:

