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
        
        """
        self.main_window.push_add_log.clicked.connect(self.addFeatureEntry)
        
        self.headers = ['Source', 'Destination', 'Summary', 'Timestamp']
        self.history_model = QtGui.QStandardItemModel()
        self.main_window.table_log_history.setModel(self.history_model)
        """

    def activated(self, item_id):

        self.active_item_id = int(item_id)
        
        # reset all widegts and populate history

    def addFeatureEntry(self):

        pass

    def reload_data(self, data):

        self.data = data


# vim: set ts=4 sw=4 ai si expandtab:

