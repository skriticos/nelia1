# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import time
from PySide.QtCore import *
from PySide.QtGui import *
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxLog:
    def __init__(self):
        self.view = dc.ui.log.v.table_history
        self.model = QStandardItemModel()
        self.view_headers = ['ID', 'Created', 'Summary']
        self.model.setHorizontalHeaderLabels(self.view_headers)
        self.view.setModel(self.model)
        self.selection_model = self.view.selectionModel()
        self.horizontal_header = self.view.horizontalHeader()
        self.view.setAlternatingRowColors(True)
        # connect add roadmap callbacks
        dc.ui.log.v.push_new_entry.clicked.connect(self.onNewEntryClicked)
        dc.ui.log_diag_new.v.accepted.connect(self.onNewSubmit)
        self.selection_model.selectionChanged.connect(self.onSelectionChange)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewEntryClicked(self):
        dc.ui.log_diag_new.v.text_detail.clear()
        dc.ui.log_diag_new.v.line_summary.clear()
        dc.ui.log_diag_new.v.show()
        dc.ui.log_diag_new.v.line_summary.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChange(self, item_selection):
        indexes = item_selection.indexes()
        if not indexes:
            dc.ui.log.v.text_detail.setEnabled(False)
            dc.ui.log.v.text_detail.setPlainText('No log selected')
            return
        row = indexes[0].row()
        # get selected log id
        index = self.model.index(row, 0)
        slogid = int(self.model.itemFromIndex(index).text())
        # populate detail widget
        dc.ui.log.v.text_detail.setEnabled(True)
        dc.ui.log.v.text_detail.setPlainText(dc.sp.log._(slogid).detail.v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        dc.c.log.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.log.header.width.v.append(self.view.columnWidth(i))
        dc.c.log.sort.column.v \
                = self.horizontal_header.sortIndicatorSection()
        dc.c.log.sort.order.v \
                = self.horizontal_header.sortIndicatorOrder().__repr__()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(dc.c.log.header.width.v):
            self.view.setColumnWidth(i, v)
        if dc.c.log.sort.column.v:
            self.horizontal_header.setSortIndicator(
                    dc.c.log.sort.column.v, convert(dc.c.log.sort.order.v))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self):
        self.saveLayout()
        self.selection_model.clear()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.view_headers)
        for lid in range(1, dc.sp.nextlid.v):
            self.model.insertRow(0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(convert(dc.sp.log._(lid).created.v)),
                QStandardItem(dc.sp.log._(lid).summary.v)
            ])
        for i in range(self.model.rowCount()):
            index = self.model.index(i, 0)
            lid = int(self.model.itemFromIndex(index).text())
            if lid == self.slogid:
                self.selection_model.select(index,
                    QItemSelectionModel.Select|QItemSelectionModel.Rows)
                break
        self.loadLayout()
        if dc.sp.nextlid.v > 1: self.view.setFocus()
        else:                   dc.ui.log.v.push_new_entry.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowTab(self):
        # check if project selection changed
        if dc.r.log.pid.last.v != dc.spid.v:
            dc.r.log.pid.last.v = dc.spid.v
            dc.ui.log.v.line_project.setText(dc.sp.name.v)
            dc.ui.log_diag_new.v.line_project.setText(dc.sp.name.v)
            self.slogid = dc.sp.nextlid.v
            self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewSubmit(self):
        lid = self.slogid = dc.sp.nextlid.v
        dc.sp.log._(lid).created.v = int(time.time())
        dc.sp.log._(lid).summary.v = dc.ui.log_diag_new.v.line_summary.text()
        dc.sp.log._(lid).detail.v \
                = dc.ui.log_diag_new.v.text_detail.toPlainText()
        dc.sp.nextlid.v += 1
        dc.m.project.v.touchProject()
        self.reloadTable()
        self.view.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

