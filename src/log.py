# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, time, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datastore import data

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
        self.table = data.w_log.table_history
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
                self.model.index(self.table.currentIndex().row(), 0)).text())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChange(self):

        if self.model.rowCount() > 0 and not self.init:
            data.w_log.text_detail.setEnabled(True)
            data.w_log.text_detail.setPlainText(
                data.project [self.pid] ['log'] [self.getSelectedLogId()] \
                ['detail']
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        """
        Internally save the layout before table reload.
        """

        self.header_width = []
        for i in range(3):
            self.header_width.append(self.table.columnWidth(i))
        if self.horizontal_header.sortIndicatorSection() < 3:
            self.sort_column = self.horizontal_header.sortIndicatorSection()
            self.sort_order = self.horizontal_header.sortIndicatorOrder()
        else:
            self.sort_column = -1
            self.sort_order = None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        """
        Restore layout when table is reloaded.
        """

        for i,v in enumerate(self.header_width):
            self.table.setColumnWidth(i, v)
        if self.sort_column != -1:
            self.horizontal_header.setSortIndicator(self.sort_column,
                                                    self.sort_order)

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
        self.model.setHorizontalHeaderLabels(self.table_headers)

        # populate table
        for i in range(data.project[self.pid]['meta']['last_log']):
            log = data.project[self.pid]['log'][i+1]
            self.model.insertRow(0, [
                QStandardItem(str(i+1).zfill(4)),
                QStandardItem(datetime.datetime.fromtimestamp(
                    log['created']).isoformat()),
                QStandardItem(log['summary'])
            ])

        # setup state
        self.table.sortByColumn(0, Qt.DescendingOrder)

        self.init = False # re-enable selection change callback
        if data.project[self.pid]['meta']['last_log'] > 0:
            self.table.selectRow(0)
            self.table.setFocus()
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

        # retrive pid
        pid = data.c_project.getSelectedProject()

        # check if project selection changed
        if data.run['log_pid_last'] != pid:

            # set data
            self.pid = pid
            data.run['log_pid_last'] = pid
            self.init = True # skip selection change callback

            # setup widget
            pname = data.c_project.getSelectedProjectName()
            data.w_log.line_project.setText(pname)
            data.w_log_diag_new.line_project.setText(pname)

            self.reloadTable()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewEntry(self):
        """
        User submits a new log entry. Add it to NxDataStrore and update view.
        """

        lid = data.project[self.pid]['meta']['last_log'] + 1
        timestamp = int(time.time())
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        # populate data
        data.project[self.pid]['log'][lid] = {
            'created': timestamp,
            'summary': data.w_log_diag_new.line_summary.text(),
            'detail':  data.w_log_diag_new.text_detail.toPlainText()
        }

        # update
        data.c_project.touchProject(timestamp)
        data.project[self.pid]['meta']['last_log'] += 1

        # populate data
        self.model.insertRow(
            0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(disptime),
                QStandardItem(data.w_log_diag_new.line_summary.text())
            ]
        )

        # update state
        self.table.selectRow(0)
        self.table.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

