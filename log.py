#! /usr/bin/env python3

import os, time, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxLog:

    def __init__(self, parent, datastore, widget):

        self.parent = parent
        self.data   = datastore
        self.widget = widget

        self.table = widget.table_history
        self.model = QStandardItemModel()
        self.table_headers = ['Created', 'Summary', 'ID']
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)
        self.table.setColumnWidth(0, 160)
        self.table.setColumnWidth(1, 550)

        self.widget.push_new_entry.clicked.connect(lambda: (
            self.parent.w_log_diag_new.line_summary.clear(),
            self.parent.w_log_diag_new.text_detail.clear(),
            self.parent.w_log_diag_new.line_summary.setFocus(),
            self.parent.w_log_diag_new.show()))

        self.parent.w_log_diag_new.accepted.connect(self.onNewEntry)

    def onShowTab(self):

        pid = self.data.run['project'].getSelectedProject()

        if self.data.run['log_pid_last'] != pid:

            self.data.run['log_pid_last'] = pid

            self.log = self.data.project[pid]['log']
            pname = self.data.run['project'].getSelectedProjectName()

            self.widget.line_project.setText(pname)
            self.parent.w_log_diag_new.line_project.setText(pname)
            self.parent.w_log_diag_detail.line_project.setText(pname)

            self.model.clear()
            self.model.setHorizontalHeaderLabels(self.table_headers)
            self.table.setColumnWidth(0, 160)
            self.table.setColumnWidth(1, 550)

            for i in range(self.data.project[pid]['meta']['last_log']):
                log = self.log[i+1]
                self.model.insertRow(0, [
                    QStandardItem(datetime.datetime.fromtimestamp(log['created']).isoformat()),
                    QStandardItem(log['summary']),
                    QStandardItem(str(i+1)) ])

            if self.data.project[pid]['meta']['last_log'] > 0:
                self.table.selectRow(0)
                self.widget.push_detail.setEnabled(True)
                self.table.sortByColumn(0, Qt.DescendingOrder)
            else:
                self.widget.push_detail.setEnabled(False)

            self.table.setFocus()

    def onNewEntry(self):

        pid = self.data.run['project'].getSelectedProject()
        lid = self.data.project[pid]['meta']['last_log'] + 1
        timestamp = int(time.time())
        d = self.parent.w_log_diag_new
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        self.data.project[pid]['log'][lid] = {
            'created': timestamp,
            'summary': d.line_summary.text(),
            'detail': d.text_detail.toPlainText()
        }

        self.model.insertRow(
            0, [
                QStandardItem(disptime),
                QStandardItem(d.line_summary.text()),
                QStandardItem(str(lid))
            ]
        )

        self.table.selectRow(0)
        self.table.setFocus()

        self.data.run['project'].touchProject(timestamp)
        self.data.project[pid]['meta']['last_log'] += 1
        self.widget.push_detail.setEnabled(True)

        '''
    ####################   UTILITY METHODS   ####################

    def getSelectedLog(self):

        run_log = self.rundat['log']

        table = run_log['table_log_history']
        model = run_log['table_model_history']

        row = table.currentIndex().row()
        index = model.index(row, 2)
        return int(model.itemFromIndex(index).text())

    ####################   CALLBACKS   ####################


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

        '''

# vim: set ts=4 sw=4 ai si expandtab:

