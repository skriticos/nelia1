#! /usr/bin/env python3


"""
Application Name: 	Nelia
Component:			Main window

This file contains the MainWindow class for Nelia.
"""

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from indextablectrl import IndexTableCtrl

from pprint import pprint

class MainWindow(QtCore.QObject):
    
    def __init__(self):
        
        super().__init__()

        # LOAD UI
        loader = QtUiTools.QUiLoader()
        uifile = QtCore.QFile('forms/mainwindow.ui')
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile)
        uifile.close()


        self.index_table_ctrl = IndexTableCtrl(self.ui.__dict__['table_root_index'])


# vim: set ts=4 sw=4 ai si expandtab:

