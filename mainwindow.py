#! /usr/bin/env python3

"""
Application Name:       Nelia
Component:                      Main window

This file contains the MainWindow class for Nelia.
"""

import os, pickle, time, gzip

from PySide import QtCore
from PySide import QtGui
from PySide import QtUiTools
from indextablectrl import IndexTableCtrl
from newchangeindex import NewChangeIndex
from logctrl import LogCtrl
from featurectrl import FeatureCtrl

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
            IndexTableCtrl(self.ui.table_root_index, self)

        # NEW/CHANGE DIALOG SETUP
        self.new_change_index = NewChangeIndex(self, self.index_table_ctrl)

        # LOG CTRL
        self.log_ctrl = LogCtrl(self, self.ui)
        self.feature_ctrl = FeatureCtrl(self, self.ui)
        
        # CONNECT SIGNALS
        self.ui.action_save_db.triggered.connect(self.save)
        self.ui.action_save_as_db.triggered.connect(self.saveAs)
        self.ui.action_open_db.triggered.connect(self.openFile)
        self.ui.table_root_index.selectionModel().selectionChanged.connect(self.indexSelectionChanged)
        self.ui.action_new_entry.triggered.connect(self.new_change_index.showCreate)
        self.ui.tabw_root.currentChanged.connect(self.tabChanged)

        # SET CONTROL STATES
        self.reset_controls()

    def getActiveProjectName(self):

        rowindex = self.ui.table_root_index.currentIndex().row()
        child = self.index_table_ctrl.model.index(rowindex, 0)
        return self.index_table_ctrl.model.itemFromIndex(child).text()

    def getIndexEntryId(self):
        
        rowindex = self.ui.table_root_index.currentIndex().row()
        child = self.index_table_ctrl.model.index(rowindex, 8)
        return self.index_table_ctrl.model.itemFromIndex(child).text()

    def tabChanged(self):

        if self.ui.tabw_root.tabText(
                self.ui.tabw_root.currentIndex()) == 'Log':
            self.log_ctrl.activated(self.getIndexEntryId())

        if self.ui.tabw_root.tabText(
                self.ui.tabw_root.currentIndex()) == 'Features':
            self.feature_ctrl.activated(self.getIndexEntryId())

    def indexSelectionChanged(self):

        rowindex = self.ui.table_root_index.currentIndex().row()
        child = self.index_table_ctrl.model.index(rowindex, 8)
        entryid = self.index_table_ctrl.model.itemFromIndex(child).text()

        self.ui.tabw_root.setTabEnabled(1, True)
        self.ui.tabw_root.setTabEnabled(2, True)

    def reset_controls(self):

        self.ui.tabw_root.setTabEnabled(1, False)
        self.ui.tabw_root.setTabEnabled(2, False)

    def save(self):

        if self.path == '':
            self.saveAs()
        
        data = {}
        data['.index_table_ctrl.data'] = self.index_table_ctrl.data
        data['.log_ctrl.data'] = self.log_ctrl.data
        data['.feature_ctrl.data'] = self.feature_ctrl.data

        pickled_data = pickle.dumps(data, 3)
        compressed_data = gzip.compress(pickled_data)

        with open(self.path, 'wb') as f:
            f.write(compressed_data)

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

        file_buffer = ''
        with open(self.path, 'rb') as f:
                file_buffer = f.read()

        decompressed = gzip.decompress(file_buffer)
        data = pickle.loads(decompressed)

        self.index_table_ctrl.reload_data(data['.index_table_ctrl.data'])
        self.log_ctrl.reload_data(data['.log_ctrl.data'])
        self.feature_ctrl.reload_data(data['.feature_ctrl.data'])


# vim: set ts=4 sw=4 ai si expandtab:

