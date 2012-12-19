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
        self.table_headers = \
                ['ID', 'Created', 'Summary']
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)

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

            self.model.clear()
            self.model.setHorizontalHeaderLabels(self.table_headers)
            self.table.setColumnWidth(1, 160)
            self.table.setColumnWidth(2, 550)

            for i in range(self.data.project[pid]['meta']['last_log']):
                log = self.log[i+1]
                self.model.insertRow(0, [
                    QStandardItem(datetime.datetime.fromtimestamp(log['created']).isoformat()),
                    QStandardItem(log['summary']),
                    QStandardItem(str(i+1)) ])

            if self.data.project[pid]['meta']['last_log'] > 0:
                self.table.selectRow(0)
                self.table.sortByColumn(0, Qt.DescendingOrder)

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

# vim: set ts=4 sw=4 ai si expandtab:

