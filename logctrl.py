#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Log Control Class

This file contains the class that controls log entries.

121103:
Some data redesign. Timestamps are not reliable id's. I have to change the data
design for log entries to look like the one in main window.
project_id (form mw) -> log_id -> keys (source, dest, summary, details, time)
"""

import time
from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools


class LogCtrl(QtCore.QObject):
    
    def __init__(self, parent, ui):
        
        super().__init__()

        self.parent = parent
        self.ui = ui

        self.data = {'lastid' : 0}

        self.ui.push_add_log.clicked.connect(self.addLogEntry)
        
        self.headers = ['Source', 'Destination', 'Summary', 'Timestamp', 'ID']
        self.history_model = QtGui.QStandardItemModel()
        self.ui.table_log_history.setModel(self.history_model)
        
        # LOG DETAILS WIDGET SETUP
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile('forms/log_details.ui')
        uifile.open(QtCore.QFile.ReadOnly)
        self.log_details = loader.load(uifile)
        uifile.close()

        # self.ui.table_log_history.activated.connect(self.showDetails)

        """
    def showDetails(self):
   
        # GET LOG ITEM
        rowindex = self.ui.table_log_history.currentIndex().row()
        child = self.history_model.index(rowindex, 4)
        entryid = self.history_model.itemFromIndex(child).text()

        # self.log_details.line_timestamp.setText(

        self.log_details.show()

        print (entryid)

        print ('show details triggered')
        pass
        """

    def activated(self, project_id):

        self.active_project_id = int(project_id)

        self.history_model.clear()
        self.history_model.setHorizontalHeaderLabels(self.headers)

        self.ui.line_log_summary.clear()
        self.ui.text_log_entry.clear()
        
        for key, entry in self.data[int(project_id)].items():
            self.history_model.appendRow([
                QtGui.QStandardItem(str(entry['source'])),
                QtGui.QStandardItem(str(entry['destination'])),
                QtGui.QStandardItem(str(entry['summary'])),
                QtGui.QStandardItem(str(entry['timestamp'])),
                QtGui.QStandardItem(str(key))
            ])

        self.ui.table_log_history.sortByColumn(3, QtCore.Qt.DescendingOrder)

    def addLogEntry(self):
  
        self.addEventLogEntry(
            self.active_project_id,
            'user', 
            'user log', 
            self.ui.line_log_summary.text(),
            self.ui.text_log_entry.toHtml())
        self.activated(self.active_project_id)

    def addEventLogEntry(self, project_id, source, destination, summary, details):

        if not int(project_id) in self.data:
            self.data[int(project_id)] = {}
        self.data[int(project_id)][self.data['lastid']] = {
                'source': source, 'destination': destination, 'summary':
                summary, 'details': details, 'timestamp': int(time.time())}
        self.data['lastid'] += 1

    def reload_data(self, data):

        self.data = data


# vim: set ts=4 sw=4 ai si expandtab:

