#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Log Control Class

This file contains the class that controls log entries.
"""

import time
from PySide import QtCore
from PySide import QtGui


class LogCtrl(QtCore.QObject):
    
    def __init__(self, parent, main_window):
        
        super().__init__()

        self.parent = parent
        self.main_window = main_window

        self.data = {}

        self.main_window.push_add_log.clicked.connect(self.addLogEntry)
        
        self.headers = ['Source', 'Destination', 'Summary', 'Timestamp']
        self.history_model = QtGui.QStandardItemModel()
        self.main_window.table_log_history.setModel(self.history_model)


    def activated(self, item_id):

        self.active_item_id = int(item_id)

        self.history_model.clear()
        self.history_model.setHorizontalHeaderLabels(self.headers)

        self.main_window.line_log_summary.clear()
        self.main_window.text_log_entry.clear()
        
        for key, entry in self.data[int(item_id)].items():
            self.history_model.appendRow([
                QtGui.QStandardItem(str(entry['source'])),
                QtGui.QStandardItem(str(entry['destination'])),
                QtGui.QStandardItem(str(entry['summary'])),
                QtGui.QStandardItem(str(key))])

        self.main_window.table_log_history.sortByColumn(3, QtCore.Qt.DescendingOrder)

    def addLogEntry(self):
  
        self.addEventLogEntry(
            self.active_item_id,
            'user', 'user log', 
            self.main_window.line_log_summary.text(),
            self.main_window.text_log_entry.toHtml())
        self.activated(self.active_item_id)

    def addEventLogEntry(self, item_id, source, destination, summary, details):

        if not int(item_id) in self.data:
            self.data[int(item_id)] = {}
        self.data[int(item_id)][int(time.time())] = {
                'source': source, 'destination': destination, 'summary': summary, 'details': details}

    def reload_data(self, data):

        self.data = data


# vim: set ts=4 sw=4 ai si expandtab:

