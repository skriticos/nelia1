#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Feature Control Class

This file contains the class that controls feature entries.
"""

import time
from PySide import QtCore
from PySide import QtGui


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
            'Timestamp'
        ]

        self.ui.push_feature_add.clicked.connect(self.addFeatureEntryManual)
        
        self.feature_model = QtGui.QStandardItemModel()
        self.ui.table_feature_list.setModel(self.feature_model)

    def activated(self, item_id):

        self.active_item_id = int(item_id)
        
        self.feature_model.clear()
        self.feature_model.setHorizontalHeaderLabels(self.headers)
        
        self.ui.line_feature_name.clear()
        self.ui.combo_feature_type.setCurrentIndex(0)
        self.ui.combo_feature_priority.setCurrentIndex(0)
        self.ui.combo_feature_target_release.setCurrentIndex(0)
        self.ui.text_feature_description.clear()

        for key, entry in self.data[int(item_id)].items():
            self.feature_model.appendRow([
                QtGui.QStandardItem(str(entry['name'])),
                QtGui.QStandardItem(str(entry['feature_type'])),
                QtGui.QStandardItem(str(entry['priority'])),
                QtGui.QStandardItem(str(entry['target_release'])),
                QtGui.QStandardItem(str(key))])

        self.ui.table_feature_list.sortByColumn(4, QtCore.Qt.DescendingOrder)

    def addFeatureEntryManual(self):
  
        self.addFeatureEntry(
            self.active_item_id,
            self.ui.line_feature_name.text(),
            self.ui.combo_feature_type.currentText(),
            self.ui.combo_feature_priority.currentText(),
            self.ui.combo_feature_target_release.currentText(),
            self.ui.text_feature_description.toHtml(),
            None
        )
        self.activated(self.active_item_id)

    def addFeatureEntry(self, item_id, name, feature_type, priority, 
                        target_release, description, dependency):

        if not int(item_id) in self.data:
            self.data[int(item_id)] = {}
        self.data[int(item_id)][int(time.time())] = {
                'name': name,
                'feature_type': feature_type,
                'priority': priority,
                'target_release': target_release,
                'description': description,
                'dependency': dependency
        }

        self.parent.log_ctrl.addEventLogEntry(
            item_id, 'user', 'features', 'Added feature {}'.format(name),
            'Added feature {} at {} with the following fields:'.format(name, int(time.time())) +
            '\nFeature Type: {}'.format(feature_type) +
            '\nPriority: {}'.format(priority) +
            '\nTarget Release: {}'.format(target_release))

    def reload_data(self, data):

        self.data = data


# vim: set ts=4 sw=4 ai si expandtab:

