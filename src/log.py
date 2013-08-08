# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import time
from PySide.QtCore import *
from PySide.QtGui import *
from datacore import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxLogStates:

    @logger('NxLogStates.enableAllCallbacks()')
    def enableAllCallbacks():

        # navi callbacks
        w = dc.ui.log.v
        w.btn_show_roadmap          .clicked.connect(NxLogStates.onShowRoadmap)
        w.btn_show_project          .clicked.connect(NxLogStates.onShowProject)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Called when view changes to log.
    # 1. Check if pid changed since last state --(no)--> return
    # 2. reload table
    # 3. set state

    @logger('NxLogStates.onShown()')
    def onShown():
        log('STUB NxLogStates.onShown()')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # switch to roadmap or project

    @logger('NxProjectStates.onShowLogs()')
    def onShowRoadmap():
        dc.ui.log.v.setParent(dc.m.mainwindow.v)
        dc.m.roadmap.states.v.onShown()
        dc.ui.main.v.setCentralWidget(dc.ui.roadmap.v)

    @logger('NxProjectStates.onShowProject()')
    def onShowProject():
        dc.ui.log.v.setParent(dc.m.mainwindow.v)
        dc.ui.main.v.setCentralWidget(dc.ui.project.v)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


headers = ['ID', 'Created', 'Summary']
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxLog:

    @logger('NxLog.__init__(self)', 'self')
    def __init__(self):

        dc.m.log.v = self
        dc.m.log.states.v = NxLogStates


        NxLogStates.enableAllCallbacks()

'''


        self.view = dc.ui.log.v.table_history
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.view.setModel(self.model)
        self.selection_model = self.view.selectionModel()
        self.horizontal_header = self.view.horizontalHeader()
        self.view.setAlternatingRowColors(True)
        dc.ui.log.v.push_new_entry.clicked.connect(self.onNewEntryClicked)
        dc.ui.log_diag_new.v.accepted.connect(self.onNewSubmit)
        self.selection_model.selectionChanged.connect(self.onSelectionChange)
        if dc.x.config.loaded.v:
            self.loadLayout()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLog.onNewEntryClicked(self)', 'self')
    def onNewEntryClicked(self):
        dc.ui.log_diag_new.v.text_detail.clear()
        dc.ui.log_diag_new.v.line_summary.clear()
        dc.ui.log_diag_new.v.show()
        dc.ui.log_diag_new.v.line_summary.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLog.onSelectionChange(self, item_selection, previous)',
            'self', 'item_selection', 'previous')
    def onSelectionChange(self, item_selection, previous):
        indexes = item_selection.indexes()
        if not indexes:
            dc.ui.log.v.text_detail.setEnabled(False)
            dc.ui.log.v.text_detail.setPlainText('No log selected')
            return
        row = indexes[0].row()
        index = self.model.index(row, 0)
        slogid = int(self.model.itemFromIndex(index).text())
        dc.ui.log.v.text_detail.setEnabled(True)
        dc.ui.log.v.text_detail.setPlainText(dc.sp.log._(slogid).detail.v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLog.saveLayout(self)', 'self')
    def saveLayout(self):
        dc.c.log.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.log.header.width.v.append(self.view.columnWidth(i))
        column = self.horizontal_header.sortIndicatorSection()
        order  = self.horizontal_header.sortIndicatorOrder().__repr__()
        dc.c.log.sort.column.v = column
        dc.c.log.sort.order.v  = order
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLog.loadLayout(self)', 'self')
    def loadLayout(self):
        for i,v in enumerate(dc.c.log.header.width.v):
            self.view.setColumnWidth(i, v)
        if dc.c.log.sort.column.v:
            self.horizontal_header.setSortIndicator(
                    dc.c.log.sort.column.v, convert(dc.c.log.sort.order.v))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLog.reloadTable(self)', 'self')
    def reloadTable(self):
        self.saveLayout()
        self.selection_model.clear()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        for lid in range(1, dc.sp.nextlid.v):
            self.model.insertRow(0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(convert(dc.sp.log._(lid).created.v)),
                QStandardItem(dc.sp.log._(lid).summary.v) ])
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
    @logger('NxLog.onShowTab(self)', 'self')
    def onShowTab(self):
        # check if project selection changed
        if dc.r.log.pid.last.v != dc.spid.v:
            dc.r.log.pid.last.v = dc.spid.v
            dc.ui.log.v.line_project.setText(dc.sp.name.v)
            dc.ui.log_diag_new.v.line_project.setText(dc.sp.name.v)
            self.slogid = dc.sp.nextlid.v
            self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('onNewSubmit(self)', 'self')
    def onNewSubmit(self):
        lid = self.slogid = dc.sp.nextlid.v
        dc.sp.log._(lid).created.v = int(time.time())
        dc.sp.log._(lid).summary.v = dc.ui.log_diag_new.v.line_summary.text()
        detail = dc.ui.log_diag_new.v.text_detail.toPlainText()
        dc.sp.log._(lid).detail.v = detail
        dc.sp.nextlid.v += 1
        dc.m.project.v.touchProject()
        self.reloadTable()
        self.view.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

