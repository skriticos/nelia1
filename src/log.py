# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, time, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datastore import data, convert

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxLog:
    """
    Handles the log widget tab.
    """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        """
        Setup data, UI and connect callbacks.
        """

        # setup table
        self.view = data.w_log.table_history
        self.model = QStandardItemModel()
        self.view_headers = \
                ['ID', 'Created', 'Summary']
        self.model.setHorizontalHeaderLabels(self.view_headers)
        self.view.setModel(self.model)
        self.selection_model = self.view.selectionModel()
        self.horizontal_header = self.view.horizontalHeader()
        self.view.setAlternatingRowColors(True)
        self.view.setColumnWidth(1, 160)
        self.view.setColumnWidth(2, 550)

        # connect add roadmap callbacks
        data.w_log.push_new_entry.clicked.connect(lambda: (
            data.w_log_diag_new.text_detail.clear(),
            data.w_log_diag_new.line_summary.clear(),
            data.w_log_diag_new.line_summary.setFocus(),
            data.w_log_diag_new.show()))
        data.w_log_diag_new.accepted.connect(self.onNewEntry)

        # update text_detail on selection change
        self.selection_model.selectionChanged.connect(self.onSelectionChange)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getSelectedLogId(self):

        # form UI table element, currently selected entry
        return int(self.model.itemFromIndex(
                self.model.index(self.view.currentIndex().row(), 0)).text())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChange(self):

        if self.model.rowCount() > 0 and not self.init:
            data.w_log.text_detail.setEnabled(True)
            data.w_log.text_detail.setPlainText(
                data.project [data.spid] ['log'] [self.getSelectedLogId()] \
                ['detail']
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        data.conf['log']['header_width'] = list()
        for i in range(3):
            data.conf['log']['header_width'].append(self.view.columnWidth(i))
        data.conf['log']['sort_column'] \
                = self.horizontal_header.sortIndicatorSection()
        data.conf['log']['sort_order'] \
                = self.horizontal_header.sortIndicatorOrder().__repr__()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(data.conf['log']['header_width']):
            self.view.setColumnWidth(i, v)
        if data.conf['log']['sort_column']:
            self.horizontal_header.setSortIndicator(
                    data.conf['log']['sort_column'],
                    convert(data.conf['log']['sort_order']))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self, state=None, preserveLayout=True):
        """
        Uses the NxDataCore data to reload the table. Used when it has to be
        updated, like load time, different project selected or adding log
        entries.
        """

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.view_headers)

        # populate table
        for lid in range(1, data.spro['meta']['next_lid']):
            log = data.spro['log'][lid]
            self.model.insertRow(0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(convert(log['created'])),
                QStandardItem(log['summary'])
            ])

        # setup state
        self.view.sortByColumn(0, Qt.DescendingOrder)

        self.init = False # re-enable selection change callback
        if data.spro['meta']['next_lid'] > 1:
            self.view.selectRow(0)
            self.view.setFocus()
        else:
            data.w_log.text_detail.setPlainText('No log selected')
            data.w_log.text_detail.setEnabled(False)
            data.w_log.push_new_entry.setFocus()

        if preserveLayout:
            self.loadLayout()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowTab(self):
        """
        When navigating to the log tab. Check if pid has been changed and reload
        data if necessary.
        """

        # check if project selection changed
        if data.run['log_pid_last'] != data.spid:

            # set data
            data.run['log_pid_last'] = data.spid
            self.init = True # skip selection change callback

            # setup widget
            data.w_log.line_project.setText(data.spro['name'])
            data.w_log_diag_new.line_project.setText(data.spro['name'])

            self.reloadTable()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewEntry(self):
        """
        User submits a new log entry. Add it to NxDataStrore and update view.
        """

        lid = data.spro['meta']['next_lid']
        timestamp = int(time.time())

        # populate data
        data.spro['log'][lid] = {
            'created': timestamp,
            'summary': data.w_log_diag_new.line_summary.text(),
            'detail':  data.w_log_diag_new.text_detail.toPlainText()
        }

        # update
        data.touchProject()
        data.spro['meta']['next_lid'] += 1

        # populate data
        self.model.insertRow(
            0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(convert(timestamp)),
                QStandardItem(data.w_log_diag_new.line_summary.text())
            ]
        )

        # update state
        self.view.selectRow(0)
        self.view.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

