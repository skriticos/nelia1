# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time

from PySide.QtCore import *
from PySide.QtGui import *

from datacore import *
from common import *
from common2 import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# STATES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class states: pass

states.startup = {
    'lbl_log_type':     {'clear': True},
    'lbl_log_created':  {'clear': True},
    'lbl_log_modified': {'clear': True},
    'btn_log_delete':   {'enabled': False},
    'text_log_message': {'enabled': False},
    'line_log_summary': {'enabled': False}
}

states.editlog = {
    'text_log_message': {'clear': True, 'enabled': True},
    'line_log_summary': {'clear': True, 'enabled': True}
}
states.noeditlogs = {
    'text_log_message': {'clear': True, 'enabled': False},
    'line_log_summary': {'clear': True, 'enabled': False}
}

states.description_normal = {
    'log_meta':       {'visible': True, 'enabled': True},
    'group_log_list': {'visible': True, 'enabled': True},
    'gl_info':        {'margins': (0, 0, 0, 0)}
}
states.description_maximized = {
    'log_meta':       {'visible': False, 'enabled': True},
    'group_log_list': {'visible': False, 'enabled': True},
    'gl_info':        {'margins': (0, 10, 15, 0)}
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALLBACK CONTROL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('(log) enableSelectionCallback()')
def enableSelectionCallback():
    pass

@logger('(log) disableSelectionCallback()')
def disableSelectionCallback():
    pass

@logger('(log) enableEditCallbacks()')
def enableEditCallbacks():
    dc.ui.log.v.line_log_summary.textChanged.connect(dc.m.log.v.onSummaryChanged)
    dc.ui.log.v.text_log_message.textChanged.connect(dc.m.log.v.onDescriptionChanged)

@logger('(log) disableEditCallbacks()')
def disableEditCallbacks():
    dc.ui.log.v.line_log_summary.textChanged.disconnect(dc.m.log.v.onSummaryChanged)
    dc.ui.log.v.text_log_message.textChanged.disconnect(dc.m.log.v.onDescriptionChanged)

@logger('(log) enableAllCallbacks()')
def enableAllCallbacks():

    w = dc.ui.log.v
    w.btn_log_new               .clicked.connect(dc.m.log.v.onNewLogClicked)

    # navi callbacks
    w = dc.ui.log.v
    w.btn_show_roadmap          .clicked.connect(onShowRoadmap)
    w.btn_show_project          .clicked.connect(onShowProject)

    w = dc.ui.log.v
    w.btn_log_maximize          .toggled.connect(onLogMaxToggled)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY CALLBACK IMPLEMENTATION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Maximize / restore callback for infox maximization toggle.

@logger('NxLog.onInfoMaxToggled(state)', 'state')
def onLogMaxToggled(state):

    if state:
        applyStates(states.description_maximized, dc.ui.log.v)
    else:
        applyStates(states.description_normal, dc.ui.log.v)

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

# Called when view changes to log.
# 1. Check if pid changed since last state --(no)--> return
# 2. reload table
# 3. set state

@logger('NxLogStates.onShown()')
def onShown():

    dc.ui.log.v.lbl_project_name.setText(dc.sp.name.v)
    loglist.reloadTable()

dc.m.log.onShown.v = onShown

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class loglist:

    headers = [
        'ID',
        'Summary'
        'Type',
        'Modified',
        'Created'
    ]

    @logger('loglist.initTable()')
    def initTable():

        dc.x.log.view.v = dc.ui.log.v.tbl_log_list
        dc.x.log.model.v = QStandardItemModel()
        dc.x.log.view.v.setModel(dc.x.log.model.v)
        dc.x.log.model.v.setHorizontalHeaderLabels(loglist.headers)
        dc.x.log.selection_model.v = dc.x.log.view.v.selectionModel()
        dc.x.log.horizontal_header.v = dc.x.log.view.v.horizontalHeader()

    # used in with setTableValue
    colLid       = 0
    colSummary   = 1
    colType      = 2
    colModified  = 3
    colCreated   = 4

    @logger('loglist.reloadTable()')
    def reloadTable():

        saveLayout('log')

        # clear table
        disableSelectionCallback()
        dc.x.log.model.v.clear()
        dc.x.log.selection_model.v.reset()
        enableSelectionCallback()
        dc.x.log.model.v.setHorizontalHeaderLabels(loglist.headers)

        if not dc.sp.log.index.v:
            loadLayout('log')
            return

        for lid in dc.sp.log.index.v:

            if dc.sp.log._(lid).ltype.v not in dc.c.log.filters.v:
                dc.x.log.slid.v = 0
                continue

            dc.x.log.model.v.insertRow(0, [
                QStandardItem(str(lid).zfill(4)),
                QStandardItem(dc.sp.log._(lid).summary.v),
                QStandardItem(dc.sp.log._(lid).ltype.v),
                QStandardItem(convert(dc.sp.log._(lid).modified.v)),
                QStandardItem(convert(dc.sp.log._(lid).created.v))
            ])

        loadLayout('log')

    """
    rowcount = dc.x.log.model.v.rowCount()
    if rowcount <= 0:
        disableEditCallbacks()
        applyStates(states.startup, dc.ui.log.v)
        return
    """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxLog:

    @logger('NxLog.__init__(self)', 'self')
    def __init__(self):

        dc.m.log.v = self

        dc.c.log.filters.v = {'User', 'Milestone', 'Track'}

        applyStates(states.startup, dc.ui.log.v)

        loglist.initTable()
        enableAllCallbacks()

    @logger('NxLog.onSummaryChanged(self)', 'self')
    def onSummaryChanged(self):
        pass

    @logger('NxLog.onDescriptionChanged(self)', 'self')
    def onDescriptionChanged(self):
        pass

    @logger('NxLog.onNewLogClicked(self)', 'self')
    def onNewLogClicked(self):

        timestamp = int(time.time())
        lid = dc.x.log.slid.v = dc.sp.nextlid.v
        dc.sp.log.index.v.add(lid)
        dc.sp.nextlid.v += 1

        dc.sp.log._(lid).created.v     = timestamp
        dc.sp.log._(lid).modified.v    = timestamp
        dc.sp.log._(lid).ltype.v       = 'User'
        dc.sp.log._(lid).summary.v     = ''
        dc.sp.log._(lid).description.v = ''

        loglist.reloadTable()

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

