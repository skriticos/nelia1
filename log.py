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

        self.widget.push_detail.clicked.connect(self.onDetailClicked)
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

    def onDetailClicked(self):

        lid = int(self.model.itemFromIndex(self.model.index(self.table.currentIndex().row(), 2)).text())
        pid = self.data.run['project'].getSelectedProject()
        log = self.data.project[pid]['log'][lid]
        disptime = datetime.datetime.fromtimestamp(log['created']).isoformat()
        d = self.parent.w_log_diag_detail
        d.line_timestamp.setText(disptime)
        d.line_summary.setText(log['summary'])
        d.text_detail.setPlainText(log['detail'])

        d.show()

# vim: set ts=4 sw=4 ai si expandtab:

