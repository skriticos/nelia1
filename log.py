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
        rd['log']['last_log_pid'] = None    # to check if reload log on tab change necessary

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
        diag_new = loader.load(uifile)
        uifile.close()
        
        run_log['diag_new'] = diag_new

        uifile = QFile('forms/log_detail.ui')
        uifile.open(QFile.ReadOnly)
        diag_detail = loader.load(uifile)
        uifile.close()
        
        run_log['diag_detail'] = diag_detail

        diag_new.setParent(run_log['ui'])
        diag_new.setWindowFlags(Qt.Dialog)
        diag_detail.setParent(run_log['ui'])
        diag_detail.setWindowFlags(Qt.Dialog)

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
        table.setColumnWidth(0, 160)
        table.setColumnWidth(1, 550)
        
        # populate data index
        run_log[':onShowTab'] = self.onShowTab
        run_log[':onNewEntryClicked'] = self.onNewEntryClicked
        run_log[':onNewEntrySubmit'] = self.onNewEntrySubmit
        run_log[':onDetailClicked'] = self.onDetailClicked
        
        run_log[':getSelectedLog'] = self.getSelectedLog
        run_log[':reset'] = self.reset

        run_log['ui_info_project_name'] = ui.line_project
        run_log['ui_cmd_new_entry'] = ui.push_new_entry
        run_log['ui_cmd_detail'] = ui.push_detail
        run_log['ui_table_history'] = ui.table_history

        run_log['ui_diag_new_info_project'] = diag_new.line_project
        run_log['ui_diag_new_input_summary'] = diag_new.line_summary
        run_log['ui_diag_new_input_detail'] = diag_new.text_detail
        
        run_log['ui_diag_detail_info_project'] = diag_detail.line_project
        run_log['ui_diag_detail_input_summary'] = diag_detail.line_summary
        run_log['ui_diag_detail_input_detail'] = diag_detail.text_detail
        run_log['ui_diag_detail_input_timestamp'] = diag_detail.line_timestamp

        # connect signals
        run_log['ui_cmd_new_entry'].clicked.connect(run_log[':onNewEntryClicked'])
        run_log['diag_new'].accepted.connect(run_log[':onNewEntrySubmit'])

        run_log['ui_cmd_detail'].clicked.connect(run_log[':onDetailClicked'])
        run_log['table_log_history'].activated.connect(
            run_log[':onDetailClicked'])

    ####################   UTILITY METHODS   #################### 

    def getSelectedLog(self):

        run_log = self.rundat['log']

        table = run_log['table_log_history']
        model = run_log['table_model_history']

        row = table.currentIndex().row()
        index = model.index(row, 2)
        return int(model.itemFromIndex(index).text())

    ####################   METHODS   #################### 

    def onShowTab(self):
        
        run_log = self.rundat['log']
        sav_log = self.savdat['log']


        pid = self.rundat['project'][':getSelectedProject']()
        
        # reset form if necessary (project selection changed or project opened)
        # note: we pretty much leave the widget alone when project selection has not
        #       changed
        
        if run_log['last_log_pid'] == None \
                or run_log['last_log_pid'] != pid:

            project_name = self.rundat['project'][':getSelectedProjectName']()
            run_log['ui_info_project_name'].setText(project_name)
            run_log['ui_diag_new_info_project'].setText(project_name)
            run_log['ui_diag_detail_info_project'].setText(project_name)
        
            table = run_log['table_log_history']
            model = run_log['table_model_history']

            model.clear()
            model.setHorizontalHeaderLabels(run_log['table_model_history_headers'])
            table.setModel(model)
            table.setColumnWidth(0, 160)
            table.setColumnWidth(1, 550)
        
            # create project id dict if not yet existent
            if pid not in sav_log['p']:
                sav_log['p'][pid] = {}              # project log container
                sav_log['p'][pid]['lastlog'] = 0    # log counter
                sav_log['p'][pid]['l'] = {}         # log entry container

            # if we have entries in log already (enable details, select first row)
            if sav_log['p'][pid]['lastlog'] > 0:

                # populate table
                for key, value in sav_log['p'][pid]['l'].items():
                    timestamp = value['timestamp']
                    summary = value['summary']
                    lid = key
                    disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()
                    run_log['table_model_history'].insertRow(0, [
                        QStandardItem(disptime),
                        QStandardItem(summary),
                        QStandardItem(str(lid))
                        ])

                # set controls
                run_log['ui_table_history'].selectRow(0)
                run_log['ui_cmd_detail'].setEnabled(True)
            else:
                run_log['ui_cmd_detail'].setEnabled(False)

            run_log['last_log_pid'] = pid
            run_log['ui_table_history'].sortByColumn(0, Qt.DescendingOrder);

        run_log['ui_table_history'].setFocus()

    ####################   CALLBACKS   #################### 

    def onNewEntryClicked(self):
    
        run_log = self.rundat['log']
        sav_log = self.savdat['log']

        run_log['ui_diag_new_input_summary'].clear()
        run_log['ui_diag_new_input_detail'].clear()

        run_log['diag_new'].show()
        
        run_log['ui_diag_new_input_summary'].setFocus()

    def onNewEntrySubmit(self):

        run_log = self.rundat['log']
        sav_log = self.savdat['log']

        pid = self.rundat['project'][':getSelectedProject']()
        lid = sav_log['p'][pid]['lastlog']

        # store changes in savdat
        timestamp = int(time.time())
        log_entry = sav_log['p'][pid]['l'][lid] = {}
        log_entry['timestamp'] = timestamp
        summary = log_entry['summary'] = run_log['ui_diag_new_input_summary'].text()
        detail = log_entry['detail'] = run_log['ui_diag_new_input_detail'].toPlainText()

        # update history table
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()
        run_log['table_model_history'].insertRow(0, [
            QStandardItem(disptime),
            QStandardItem(summary),
            QStandardItem(str(lid))
            ])
        
        sav_log['p'][pid]['lastlog'] += 1
        
        self.rundat['project'][':updateTimestamp'](timestamp)

        run_log['ui_table_history'].selectRow(0)
        run_log['ui_table_history'].setFocus()

        run_log['ui_cmd_detail'].setEnabled(True)
        self.rundat['project']['changed'] = True

    def onDetailClicked(self):

        run_log = self.rundat['log']
        sav_log = self.savdat['log']
        
        # retrive active log entry
        lid = run_log[':getSelectedLog']()
        log_entry = sav_log['p'][run_log['last_log_pid']]['l'][lid]
        disptime = datetime.datetime.fromtimestamp(log_entry['timestamp']).isoformat()

        # populate detail dialog
        run_log['ui_diag_detail_input_timestamp'].setText(disptime)
        run_log['ui_diag_detail_input_summary'].setText(log_entry['summary'])
        run_log['ui_diag_detail_input_detail'].setPlainText(log_entry['detail'])

        run_log['diag_detail'].show()

    def reset(self):
    
        # ensure log is reloaded when switched to after opening
        self.rundat['log']['last_log_pid'] = None

# vim: set ts=4 sw=4 ai si expandtab:

