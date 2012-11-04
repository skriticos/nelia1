#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Feature Control Class

This file contains the class that controls feature entries.
"""

import time
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools


class FeatureCtrl(QtCore.QObject):
    
    def __init__(self, parent, ui):
        
        super().__init__()

        self.parent = parent
        self.ui = ui

        self.data = {}
        
        self.headers = [
            'Name', 
            'Type', 
            'Priority', 
            'Target Rel.', 
            'Status',
            'Timestamp',
            'Id'
        ]

        self.ui.push_feature_add.clicked.connect(self.addFeatureEntryManual)
        
        self.feature_model = QtGui.QStandardItemModel()
        self.ui.table_feature_list.setModel(self.feature_model)
        
        # FEATURE DETAILS WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile('forms/feature_details.ui')
        uifile.open(QtCore.QFile.ReadOnly)
        self.feature_details = loader.load(uifile)
        uifile.close()
        
        self.ui.table_feature_list.activated.connect(self.showFeatureDetails)

    def showFeatureDetails(self):

        # GET FEATURE ITEM
        rowindex = self.ui.table_feature_list.currentIndex().row()
        child = self.feature_model.index(rowindex, 6)
        feature_id = int(self.feature_model.itemFromIndex(child).text())

        project_id = self.active_project_id
        feature_entry = self.data[project_id][feature_id]

        project_name = self.parent.getActiveProjectName()


        self.feature_details.line_project_name.setText(project_name)
        self.feature_details.line_priority.setText(feature_entry['priority'])
        self.feature_details.line_status.setText(feature_entry['status'])
        self.feature_details.line_name.setText(feature_entry['name'])
        self.feature_details.line_target_release.setText(feature_entry['target_release'])
        self.feature_details.line_timestamp.setText(str(feature_entry['timestamp']))
        self.feature_details.line_type.setText(feature_entry['feature_type'])
        self.feature_details.text_details.setDocument(QtGui.QTextDocument(feature_entry['description']))

        self.feature_details.show()


    def activated(self, project_id):

        self.active_project_id = int(project_id)
        
        self.feature_model.clear()
        self.feature_model.setHorizontalHeaderLabels(self.headers)
        
        self.ui.line_feature_name.clear()
        self.ui.combo_feature_type.setCurrentIndex(0)
        self.ui.combo_feature_priority.setCurrentIndex(0)
        self.ui.combo_feature_target_release.setCurrentIndex(0)
        self.ui.text_feature_description.clear()

        # in case no features have been added yet (to avoid trace message)
        if not self.active_project_id in self.data:
            return

        for key, entry in self.data[int(project_id)].items():
            if isinstance(key, int):
                self.feature_model.appendRow([
                    QtGui.QStandardItem(str(entry['name'])),
                    QtGui.QStandardItem(str(entry['feature_type'])),
                    QtGui.QStandardItem(str(entry['priority'])),
                    QtGui.QStandardItem(str(entry['target_release'])),
                    QtGui.QStandardItem(str(entry['status'])),
                    QtGui.QStandardItem(str(entry['timestamp'])),
                    QtGui.QStandardItem(str(key))])

        self.ui.table_feature_list.sortByColumn(5, QtCore.Qt.DescendingOrder)

    def addFeatureEntryManual(self):
  
        self.addFeatureEntry(
            self.active_project_id,
            self.ui.line_feature_name.text(),
            self.ui.combo_feature_type.currentText(),
            self.ui.combo_feature_priority.currentText(),
            self.ui.combo_feature_target_release.currentText(),
            self.ui.text_feature_description.toPlainText(),
            None
        )
        self.activated(self.active_project_id)

    def addFeatureEntry(self, project_id, name, feature_type, priority, 
                        target_release, description, dependency):

        project_id = int(project_id)

        if not project_id in self.data:
            self.data[project_id] = {'lastid': 0}

        self.data[project_id][self.data[project_id]['lastid']] = {
                'name': name,
                'feature_type': feature_type,
                'priority': priority,
                'target_release': target_release,
                'description': description,
                'dependency': dependency,
                'status': 'planned',
                'timestamp': int(time.time())
        }

        self.data[project_id]['lastid'] += 1

        self.parent.log_ctrl.addEventLogEntry(
            project_id, 'user', 'features', 'Added feature {}'.format(name),
            'Added feature "{}" at {} with the following fields:'.format(name, int(time.time())) +
            '\nFeature Type: {}'.format(feature_type) +
            '\nPriority: {}'.format(priority) +
            '\nTarget Release: {}'.format(target_release))

    def reload_data(self, data):

        self.data = data

# vim: set ts=4 sw=4 ai si expandtab:

