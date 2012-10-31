#! /usr/bin/env python3


"""
Application Name: 	Nelia
Component:			Index Table Control

This file contains the table model that displays information on the
project index.
"""

from PySide import QtCore
from PySide import QtGui

class IndexTableCtrl(QtCore.QObject):
    
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


# vim: set ts=4 sw=4 ai si expandtab:

