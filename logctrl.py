#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Log Control Class

This file contains the class that controls log entries.
"""

from PySide import QtCore
from PySide import QtGui


class LogCtrl(QtCore.QObject):
    
    def __init__(self, parent, main_window):
        
        super().__init__()

        self.parent = parent
        self.main_window = main_window

        self.data = {}

        self.main_window.push_add_log.clicked.connect(self.addLogEntry)

    def addLogEntry(self):
        
        print ('addLogEntry')
    
    def reload_data(self, data):

        pass


# vim: set ts=4 sw=4 ai si expandtab:

