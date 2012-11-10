#! /usr/bin/env python3

import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxLog(QObject):
    
    def __init__(self, savdat, rundat):
        
        super().__init__()

        sd = self.savdat = savdat
        rd = self.rundat = rundat
        
        rd['modules'].append('log')
        rd['log'] = {}

        sd['log'] = {}          # log save base
        sd['log']['p'] = {}     # log for projects

        run_log = rd['log']
        sav_log = sd['log']

        # mainwindow widget setup
        loader = QtUiTools.QUiLoader()
        uifile = QFile('forms/log.ui')
        uifile.open(QFile.ReadOnly)
        ui = loader.load(uifile)
        uifile.close()

        parent_widget = rd['mainwindow']['tab_log']
        ui.setParent(parent_widget)
        grid = QGridLayout()
        grid.addWidget(ui, 0, 0)
        grid.setContentsMargins(0, 5, 0, 0)
        parent_widget.setLayout(grid)
        
        # pre-populate data index
        run_log['ui'] = ui
        run_log['self'] = self

        # new project dialog setup
        uifile = QFile('forms/log_new_entry.ui')
        uifile.open(QFile.ReadOnly)
        new_diag = loader.load(uifile)
        uifile.close()
        
        uifile = QFile('forms/log_detail.ui')
        uifile.open(QFile.ReadOnly)
        detail_diag = loader.load(uifile)
        uifile.close()

        new_diag.setParent(run_log['ui'])
        new_diag.setWindowFlags(Qt.Dialog)
        detail_diag.setParent(run_log['ui'])
        detail_diag.setWindowFlags(Qt.Dialog)

        # setup project table
        table = run_log['table_log_history'] = ui.table_history
        model = run_log['table_model_history'] = QStandardItemModel()

        history_headers = \
            run_log['table_model_history_headers'] = \
                ['Timestamp', 
                 'Summary', 
                 'ID']

        model.setHorizontalHeaderLabels(history_headers)
        table.setModel(model)
        
        # populate data index
        run_log[':onShowTab'] = self.onShowTab

        run_log['ui_info_project_name'] = ui.line_project
        run_log['ui_cmd_new_entry'] = ui.push_new_entry
        run_log['ui_cmd_detail'] = ui.push_detail
        run_log['ui_table_history'] = ui.table_history

    ####################   METHODS   #################### 

    def onShowTab(self):

        run_log = self.rundat['log']
        sav_log = self.savdat['log']

        run_log['ui_info_project_name'].setText(self.rundat['project'][':getSelectedProjectName']())

    ####################   CALLBACKS   #################### 

    def onNewEntryButton(self):
    
        run_log = self.rundat['log']
        sav_log = self.savdat['log']

# vim: set ts=4 sw=4 ai si expandtab:

