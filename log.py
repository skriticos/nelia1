#! /usr/bin/env python3

import os, time, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

class NxLog:

    def __init__(self, parent, datastore, widget):

        # setup backbone
        self.parent = parent
        self.data   = datastore
        self.widget = widget

        self.diag_new = self.parent.w_log_diag_new

        # setup table
        self.table = widget.table_history
        self.model = QStandardItemModel()
        self.table_headers = \
                ['ID', 'Created', 'Summary']
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 550)

        # connect add roadmap callbacks
        self.widget.push_new_entry.clicked.connect(lambda: (
            self.parent.w_log_diag_new.text_detail.clear(),
            self.parent.w_log_diag_new.line_summary.clear(),
            self.parent.w_log_diag_new.line_summary.setFocus(),
            self.parent.w_log_diag_new.show()))
        self.parent.w_log_diag_new.accepted.connect(self.onNewEntry)

        # update text_detail on selection change
        self.selection_model.selectionChanged.connect(self.onSelectionChange)

    def getSelectedLogId(self):

        return int(self.model.itemFromIndex(
                self.model.index(self.table.currentIndex().row(), 0)).text())

    def onSelectionChange(self):

        if self.model.rowCount() > 0 and not self.init:
            self.widget.text_detail.setEnabled(True)
            self.widget.text_detail.setPlainText(
                self.data.project[self.pid] ['log'] [self.getSelectedLogId()] ['detail']
            )

    def saveLayout(self):

        self.header_width = []
        for i in range(3):
            self.header_width.append(self.table.columnWidth(i))
        if self.horizontal_header.sortIndicatorSection() < 3:
            self.sort_column = self.horizontal_header.sortIndicatorSection()
            self.sort_order = self.horizontal_header.sortIndicatorOrder()
        else:
            self.sort_column = -1
            self.sort_order = None

    def loadLayout(self):

        for i,v in enumerate(self.header_width):
            self.table.setColumnWidth(i, v)
        if self.sort_column != -1:
            self.horizontal_header.setSortIndicator(self.sort_column, self.sort_order)

    def reloadTable(self, state=None, preserveLayout=True):

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.table_headers)

        # populate table
        for i in range(self.data.project[self.pid]['meta']['last_log']):
            log = self.data.project[self.pid]['log'][i+1]
            self.model.insertRow(0, [
                QStandardItem(str(i+1).zfill(4)),
                QStandardItem(datetime.datetime.fromtimestamp(log['created']).isoformat()),
                QStandardItem(log['summary'])
            ])

        # setup state
        self.table.sortByColumn(0, Qt.DescendingOrder)

        self.init = False # re-enable selection change callback
        if self.data.project[self.pid]['meta']['last_log'] > 0:
            self.table.selectRow(0)
            self.table.setFocus()
        else:
            self.widget.text_detail.setPlainText('No log selected')
            self.widget.text_detail.setEnabled(False)
            self.widget.push_new_entry.setFocus()

        if preserveLayout:
            self.loadLayout()


    def onShowTab(self):

        # retrive pid
        pid = self.data.run['project'].getSelectedProject()

        # check if project selection changed
        if self.data.run['log_pid_last'] != pid:

            # set data
            self.pid = pid
            self.data.run['log_pid_last'] = pid
            self.init = True # skip selection change callback

            # setup widget
            pname = self.data.run['project'].getSelectedProjectName()
            self.widget.line_project.setText(pname)
            self.parent.w_log_diag_new.line_project.setText(pname)

            self.reloadTable()


    def onNewEntry(self):

        lid = self.data.project[self.pid]['meta']['last_log'] + 1
        timestamp = int(time.time())
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        # populate data
        self.data.project[self.pid]['log'][lid] = {
            'created': timestamp,
            'summary': self.diag_new.line_summary.text(),
            'detail':  self.diag_new.text_detail.toPlainText()
        }

        # update
        self.data.run['project'].touchProject(timestamp)
        self.data.project[self.pid]['meta']['last_log'] += 1

        # populate data
        self.model.insertRow(
            0, [
                QStandardItem(str(lid)),
                QStandardItem(disptime),
                QStandardItem(self.diag_new.line_summary.text())
            ]
        )

        # update state
        self.table.selectRow(0)
        self.table.setFocus()

