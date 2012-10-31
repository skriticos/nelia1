#! /usr/bin/env python3


"""
Application Name: 	Nelia
Component:			Index Table Control

This file contains the table model that displays information on the
project index.
"""

import time

from PySide import QtCore
from PySide import QtGui

class IndexTableCtrl(QtCore.QObject):
    
    """
        Stores the data for the main listing and contains the 
        interactions with the table.
    """

    def __init__(self, table_view):
        
        super().__init__()

        self.view = table_view
        self.model = QtGui.QStandardItemModel()
        self.headers = [
            'Name', 
            'Entry Type', 
            'Status', 
            'Category', 
            'Priority', 
            'Challenge', 
            'Version', 
            'Last Changed', 
            'ID' ]
        self.model.setHorizontalHeaderLabels(self.headers)
        self.data = {'lastid' : 0}
        self.view.setModel(self.model)

    def reload_data(self, data):

        self.data = data
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.headers)
        
        for key in self.data:
            if isinstance(key, int):
                self.model.appendRow([
                    QtGui.QStandardItem(str(self.data[key][0])),
                    QtGui.QStandardItem(str(self.data[key][1])),
                    QtGui.QStandardItem(str(self.data[key][2])),
                    QtGui.QStandardItem(str(self.data[key][3])),
                    QtGui.QStandardItem(str(self.data[key][4])),
                    QtGui.QStandardItem(str(self.data[key][5])),
                    QtGui.QStandardItem(str(self.data[key][5])),
                    QtGui.QStandardItem(str(self.data[key][7])),
                    QtGui.QStandardItem(str(key))
                ])

    def removeActiveRow(self):
    
        rowindex = self.currentIndex().row()
        child = self.model.index(rowindex, 8) # 8 = ID column
        entryid = self.model.itemFromIndex(child).text()
        del self.data[int(entryid)]
        self.model.removeRow(rowindex)

    def addNewRow(self, name, entrytype, category, priority, challange):

        entryid = self.data['lastid'] + 1
        entry = [
            name, entrytype, 'Spark', category,
            priority, challange, '0.0.0',
            int(time.time())
        ]

        self.data[entryid] = entry
        self.data['lastid'] += 1
        
        self.model.appendRow([
            QtGui.QStandardItem(name),
            QtGui.QStandardItem(entrytype),
            QtGui.QStandardItem('Spark'),
            QtGui.QStandardItem(category),
            QtGui.QStandardItem(str(priority)),
            QtGui.QStandardItem(str(challange)),
            QtGui.QStandardItem('0.0.0'),
            QtGui.QStandardItem(str(int(time.time()))),
            QtGui.QStandardItem(str(entryid))
        ])
    
    def changeRow(self, itemid, rowindex, name, entrytype, 
                  category, priority, challange):

        status = self.model.itemFromIndex(
            self.model.index(rowindex, 2)).text()
        
        version = self.model.itemFromIndex(
            self.model.index(rowindex, 6)).text()
        
        entry = [
            name, entrytype, status, category,
            priority, challange, version,
            int(time.time())
        ]

        self.data[itemid] = entry

        tabdat = (
            (0, name), 
            (1, entrytype),
            (2, status),
            (3, category),
            (4, priority),
            (5, challange),
            (6, version),
            (7, int(time.time())),
            (8, itemid)
        )

        for index, value in tabdat:
            self.model.setData(
                self.model.index(rowindex, index), value)


# vim: set ts=4 sw=4 ai si expandtab:

