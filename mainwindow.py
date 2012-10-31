#! /usr/bin/env python3


"""
Application Name: 	Nelia
Component:			Main window

This file contains the MainWindow class for Nelia.
"""

import os, pickle, time

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from indextablectrl import IndexTableCtrl
from newchangeindex import NewChangeIndex
from logctrl import LogCtrl

from pprint import pprint

class MainWindow(QtCore.QObject):
    
    def __init__(self):
        
        super().__init__()
        self.path = ''

        loader = QtUiTools.QUiLoader()
        
        # MAINWINDOW WIDGET SETUP
        uifile = QtCore.QFile('forms/mainwindow.ui')
        uifile.open(QtCore.QFile.ReadOnly)
        self.ui = loader.load(uifile)
        uifile.close()
        self.ui.setWindowIcon(QtGui.QIcon('img/icon.png'))
        
        self.index_table_ctrl = \
            IndexTableCtrl(self.ui.table_root_index)

        # NEW/CHANGE DIALOG SETUP
        self.new_change_index = NewChangeIndex(self.index_table_ctrl)

        # LOG CTRL
        self.log_ctrl = LogCtrl(self, self.ui)
        
        # CONNECT SIGNALS
        self.ui.action_save_db.triggered.connect(self.save)
        self.ui.action_save_as_db.triggered.connect(self.saveAs)
        self.ui.action_open_db.triggered.connect(self.openFile)

        self.ui.action_new_entry.triggered.connect(
            self.new_change_index.showCreate)
        
    def save(self):

        if self.path == '':
            self.saveAs()
        
        data = {}
        data['.index_table_ctrl.data'] = self.index_table_ctrl.data
        data['.log_ctrl.data'] = self.log_ctrl.data

        with open(self.path, 'wb') as f:
            pickle.dump(data, f, 3)

    def saveAs(self):

        file_name = QtGui.QFileDialog.getSaveFileName(
            self.ui, 
            'Save Nelia file', 
            os.path.expanduser('~/Documents/save.nelia'), 
            'Nelia Files (*.nelia)')[0]

        if file_name.rfind('.nelia') != len(file_name) - 6:
            file_name += '.nelia'

        self.path = file_name
        self.save()

    def openFile(self):
    
        self.path = QtGui.QFileDialog.getOpenFileName(
            self.ui, 'Open Nelia file', 
            os.path.expanduser('~/Documents'), 
            'Nelia Files (*.nelia)')[0]

        data = {}
        with open(self.path, 'rb') as f:
            data = pickle.load(f)

        self.index_table_ctrl.reload_data(data['.index_table_ctrl.data'])
        self.log_ctrl.reload_data(data['.log_ctrl.data'])


# vim: set ts=4 sw=4 ai si expandtab:

