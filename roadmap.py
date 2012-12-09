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
            ['Name', 'Target', 'Prio.', 'Type', 'Compl.', 'ID']
        self.issue_headers = \
            ['Name', 'Target', 'Prio.', 'Sev.', 'Closed', 'ID']

        self.model_feature = QStandardItemModel()
        self.table_feature = self.widget.table_feature
        self.table_feature.setModel(self.model_feature)
        self.model_issue = QStandardItemModel()
        self.table_issue = self.widget.table_issue
        self.table_issue.setModel(self.model_issue)

    def onShowTab(self):

        pid = self.data.run['project'].getSelectedProject()
        if self.data.run['roadmap_pid_last'] == 0 or self.data.run['roadmap_pid_last'] != pid:

            pro = self.data.project[pid]

            project_name = self.data.run['project'].getSelectedProjectName()
            self.widget.line_project.setText(project_name)
            self.parent.w_roadmap_diag_add_feature.line_project.setText(project_name)
            self.parent.w_roadmap_diag_add_issue.line_project.setText(project_name)

            x, y = pro['meta']['current_milestone']
            milestones = pro['milestone']

            self.widget.gridLayout_2.removeWidget(self.widget.push_milestone)
            self.widget.push_milestone.close()
            self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection)
            self.widget.gridLayout_2.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
            self.widget.label_2.setBuddy(self.widget.push_milestone)

            self.reloadTables()

            self.widget.push_add_feature.clicked.connect(self.showAddFeature)
            self.parent.w_roadmap_diag_add_feature.accepted.connect(self.onSubmitNewFeature)

            # computing next_x, next_y is quite tricky, so we take it from the milestone widget (which does it anyway)
            self.selected_x = self.widget.push_milestone.next_x
            self.selected_y = self.widget.push_milestone.next_y

            # TODO: POPULATE TABLES ON TAB SWITCH

    def onChangeVersionSelection(self, x, y, current_text):

        self.selected_x = x
        self.selected_y = y

        self.reloadTables()

    def reloadTables(self):

        self.selected_x, self.selected_y = self.widget.push_milestone.getVersion()

        self.parent.w_roadmap_diag_add_feature.radio_secondary.setChecked(False)
        self.parent.w_roadmap_diag_add_feature.radio_primary.setChecked(True)
        self.parent.w_roadmap_diag_add_feature.spin_priority.setValue(50)

        self.model_feature.clear()
        self.model_feature.setHorizontalHeaderLabels(self.feature_headers)
        self.table_feature.setColumnWidth(0, 180)
        self.table_feature.setColumnWidth(1, 50)
        self.table_feature.setColumnWidth(2, 50)
        self.table_feature.setColumnWidth(3, 70)
        self.table_feature.setColumnWidth(4, 68)
        self.table_feature.setColumnWidth(5, 50)

        self.model_issue.clear()
        self.model_issue.setHorizontalHeaderLabels(self.issue_headers)
        self.table_issue.setColumnWidth(0, 200)
        self.table_issue.setColumnWidth(1, 50)
        self.table_issue.setColumnWidth(2, 50)
        self.table_issue.setColumnWidth(3, 50)
        self.table_issue.setColumnWidth(4, 68)
        self.table_issue.setColumnWidth(5, 50)

        # TODO: reload feature / issue tables

    def showAddFeature(self):

        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        x, y = self.data.project[pid]['meta']['current_milestone']
        d = self.parent.w_roadmap_diag_add_feature

        d.gridLayout_2.removeWidget(d.push_target_milestone)
        d.push_target_milestone.close()
        d.push_target_milestone \
                = MPushButton(x,y,milestones,d,None,self.selected_x,self.selected_y)
        d.gridLayout_2.addWidget(d.push_target_milestone, 1, 1, 1, 1);

        d.line_name.clear()
        d.text_description.clear()
        d.show()
        d.line_name.setFocus()

    def onSubmitNewFeature(self):

        pid = self.data.run['project'].getSelectedProject()
        milestones = self.data.project[pid]['milestone']
        d = self.parent.w_roadmap_diag_add_feature
        x, y = self.data.project[pid]['meta']['current_milestone']
        target_label = d.push_target_milestone.text()
        tx, ty = target_label.split(' ')[3][1:].split('.')
        tx = int(tx)
        ty = int(ty)
        timestamp = int(time.time())

        if d.radio_primary.isChecked():
            ftype = 'Primary'
        else:
            ftype = 'Secondary'

        name = d.line_name.text()
        priority = d.spin_priority.value()
        description = d.text_description.toPlainText()

        new_feature = {
            'name':         d.line_name.text(),
            'priority':     d.spin_priority.value(),
            'type':         ftype,
            'description':  d.text_description.toPlainText(),
            'created':      timestamp,
            'completed':    False
        }

        # only add feature, if added to currently selected version
        if tx == self.selected_x and ty == self.selected_y:
            # add to feature table
            model = self.model_feature
            model.insertRow(0, [
                QStandardItem(name),
                QStandardItem('{}.{}'.format(tx,ty)),
                QStandardItem(str(priority)),
                QStandardItem(ftype),
                QStandardItem('No'),
                QStandardItem(str(self.data.project[pid]['meta']['last_feature']+1))
            ])

        # save new feature data
        if tx == 0:
            ty -= 1

        """
        # FIXME: incomplete
        if len(milestones) == tx+1: # new major version
            pass
        elif len(milestones[tx]) == ty+1: # new minor version
            milestones.append({'m': '{}.{}'.format(tx, ty+2), 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}),
        """

        self.data.project[pid]['milestone'][tx][ty]['fo'][self.data.project[pid]['meta']['last_feature']+1] = new_feature
        self.data.project[pid]['meta']['last_feature'] += 1

        self.widget.gridLayout_2.removeWidget(self.widget.push_milestone)
        self.widget.push_milestone.close()
        self.widget.push_milestone = MPushButton(x, y, milestones, self.widget, self.onChangeVersionSelection, self.selected_x, self.selected_y)
        self.widget.gridLayout_2.addWidget(self.widget.push_milestone, 0, 1, 1, 1)
        self.widget.label_2.setBuddy(self.widget.push_milestone)

# vim: set ts=4 sw=4 ai si expandtab:

