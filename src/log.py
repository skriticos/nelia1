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
    'text_log_message': {'clear': True, 'enabled': False},
    'line_log_summary': {'clear': True, 'enabled': False}
}

states.selected = {
    'text_log_message': {'clear': True, 'enabled': True},
    'line_log_summary': {'clear': True, 'enabled': True},
    'btn_log_delete' :  {'enabled': True}
}

states.user = {
    'text_log_message': {'enabled': True},
    'line_log_summary': {'enabled': True}
}

states.nonuser = {
    'text_log_message': {'enabled': False},
    'line_log_summary': {'enabled': False}
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

    m = dc.x.log.selection_model.v
    m.selectionChanged.connect(onSelectionChanged)

@logger('(log) disableSelectionCallback()')
def disableSelectionCallback():

    m = dc.x.log.selection_model.v
    m.selectionChanged.disconnect(onSelectionChanged)

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
    w.btn_log_delete            .clicked.connect(dc.m.log.v.onDeleteLogClicked)

    # navi callbacks
    w = dc.ui.log.v
    w.btn_show_roadmap          .clicked.connect(onShowRoadmap)
    w.btn_show_project          .clicked.connect(onShowProject)

    w = dc.ui.log.v
    w.btn_log_maximize          .toggled.connect(onLogMaxToggled)

    # filter callbacks
    dc.ui.log.v.btn_log_user        .toggled.connect(onFilterUserToggled)
    dc.ui.log.v.btn_log_milestone   .toggled.connect(onFilterMilestoneToggled)
    dc.ui.log.v.btn_log_tracking    .toggled.connect(onFilterTrackToggled)

    # edit callbacks
    enableEditCallbacks()
    enableSelectionCallback()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY CALLBACK IMPLEMENTATION
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Maximize / restore callback for infox maximization toggle.

@logger('(log) onInfoMaxToggled(state)', 'state')
def onLogMaxToggled(state):

    if state:
        applyStates(states.description_maximized, dc.ui.log.v)
    else:
        applyStates(states.description_normal, dc.ui.log.v)


### FILTER TOGGLE CALLBACKS ###

@logger('(log) onFilterUserToggled(checked)', 'checked')
def onFilterUserToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.log.filters.v.add('User')
    else:
        dc.c.log.filters.v.discard('User')
    loglist.reloadTable()

@logger('(log) onFilterMilestoneToggled(checked)', 'checked')
def onFilterMilestoneToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.log.filters.v.add('Milestone')
    else:
        dc.c.log.filters.v.discard('Milestone')
    loglist.reloadTable()

@logger('(log) onFilterTrackToggled(checked', 'checked')
def onFilterTrackToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.log.filters.v.add('Track')
    else:
        dc.c.log.filters.v.discard('Track')
    loglist.reloadTable()

@logger('(log) onSelectionChange(new, old)', 'new', 'old')
def onSelectionChanged(new, old):

    # check for valid index
    indexes = new.indexes()
    if not indexes:
        return

    # get selected lid from table model
    index = indexes[0]
    slid = dc.x.log.slid.v = int(dc.x.log.model.v.itemFromIndex(index).text())

    # populate edit fields on selection change
    disableEditCallbacks()
    dc.ui.log.v.lbl_log_type.setText(dc.sp.log._(slid).ltype.v)
    dc.ui.log.v.lbl_log_created.setText(convert(dc.sp.log._(slid).created.v))
    dc.ui.log.v.lbl_log_modified.setText(convert(dc.sp.log._(slid).modified.v))
    dc.ui.log.v.line_log_summary.setText(dc.sp.log._(slid).summary.v)
    dc.ui.log.v.text_log_message.setText(dc.sp.log._(slid).description.v)

    if dc.sp.log._(slid).ltype.v == 'User':
        applyStates(states.user, dc.ui.log.v)
    else:
        applyStates(states.nonuser, dc.ui.log.v)

    enableEditCallbacks()


### NAVI CALLBACKS ###

@logger('(log) onShowLogs()')
def onShowRoadmap():

    dc.ui.log.v.setParent(dc.m.mainwindow.v)
    dc.m.roadmap.cbaux.v.onShow()
    dc.ui.main.v.setCentralWidget(dc.ui.roadmap.v)

@logger('(log) onShowProject()')
def onShowProject():

    dc.ui.log.v.setParent(dc.m.mainwindow.v)
    dc.ui.main.v.setCentralWidget(dc.ui.project.v)
    dc.m.project.util.v.onShow()

# Called when view changes to log.

@logger('(log) onShown()')
def onShown():

    if dc.x.lpid.v != dc.spid.v:
        dc.x.lpid.v = dc.spid.v

        dc.ui.log.v.lbl_project_name.setText(dc.sp.name.v)
        loglist.reloadTable()

dc.m.log.onShown.v = onShown

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class loglist: pass

loglist.headers = [
    'ID',
    'Summary',
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

@logger('loglist.initLogFilterControls()')
def initLogFilterControls():

    # restore table sorting and headers
    loadLayout('log')

    # restore filter control states
    if 'User' in dc.c.log.filters.v:
        dc.ui.log.v.btn_log_user.setChecked(True)
    if 'Track' in dc.c.log.filters.v:
        dc.ui.log.v.btn_log_tracking.setChecked(True)
    if 'Milestone' in dc.c.log.filters.v:
        dc.ui.log.v.btn_log_milestone.setChecked(True)

# used in with setTableValue
loglist.colLid       = 0
loglist.colSummary   = 1
loglist.colType      = 2
loglist.colModified  = 3
loglist.colCreated   = 4

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
        applyStates(states.startup, dc.ui.log.v)
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

    # we don't select anything if we don't have rows
    rowcount = dc.x.log.model.v.rowCount()
    if rowcount <= 0:

        applyStates(states.startup, dc.ui.log.v)
        return

    # we don't have a selected log id (outside the filter or deleted)
    if not dc.x.log.slid.v:

        index = dc.x.log.model.v.index(0, 0)
        lid   = int(dc.x.log.model.v.data(index))
        dc.x.log.slid.v = lid

        disableEditCallbacks()
        applyStates(states.selected, dc.ui.log.v)
        enableEditCallbacks()

        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.log.selection_model.v.setCurrentIndex(index, s|r)
        selection = dc.x.log.view.v.selectionModel().selection()

        return

    # iterate through table rows
    for rowcnt in range(dc.x.log.model.v.rowCount()):

        index = dc.x.log.model.v.index(rowcnt, 0)
        lid = int(dc.x.log.model.v.data(index))

        # if we have a match, select it and abort
        if lid == dc.x.log.slid.v:

            disableEditCallbacks()
            applyStates(states.selected, dc.ui.log.v)
            enableEditCallbacks()

            s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
            dc.x.log.selection_model.v.setCurrentIndex(index, s|r)
            selection = dc.x.log.view.v.selectionModel().selection()
            break

loglist.initTable = initTable
loglist.initLogFilterControls = initLogFilterControls
loglist.reloadTable = reloadTable
dc.m.log.loglist.v = loglist

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EVENT FILTERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class EfLogDescriptionFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.log.changeflag.log_description.v:
                slid = dc.x.log.slid.v
                description = dc.ui.log.v.text_log_message.toHtml()
                dc.sp.log._(slid).description.v = description
            dc.x.log.changeflag.log_description.v = False
        return QObject.eventFilter(self, obj, event)
ef_log_desription_focus_out = EfLogDescriptionFocusOut()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxLog:

    @logger('NxLog.__init__(self)', 'self')
    def __init__(self):

        dc.m.log.v = self
        if not isinstance(dc.c.log.filters.v, set):
            dc.c.log.filters.v = {'User', 'Milestone', 'Track'}
        applyStates(states.startup, dc.ui.log.v)
        loglist.initTable()
        enableAllCallbacks()

        dc.x.log.changeflag.log_description.v = False
        dc.ui.log.v.text_log_message.installEventFilter(ef_log_desription_focus_out)

    @logger('NxLog.touchLog(self)', 'self')
    def touchLog(self):

        timestamp = int(time.time())
        lid = dc.x.log.slid.v
        dc.sp.log._(lid).modified.v = timestamp
        x = convert(timestamp)
        setTableValue('log', loglist.colModified, x)
        dc.ui.log.v.lbl_log_modified.setText(x)
        dc.m.project.v.touchProject()

    @logger('NxLog.onSummaryChanged(self, summary)', 'self', 'summary')
    def onSummaryChanged(self, summary):

        if dc.auto.v:
            return

        lid = dc.x.log.slid.v
        dc.sp.log._(lid).summary.v = summary
        setTableValue('log', loglist.colSummary, summary)
        self.touchLog()

    @logger('NxLog.onDescriptionChanged(self)', 'self')
    def onDescriptionChanged(self):

        if dc.auto.v:
            return

        self.touchLog()
        dc.x.log.changeflag.log_description.v = True

    @logger('NxLog.onNewLogClicked(self)', 'self')
    def onNewLogClicked(self):

        self.addAutoLog('User', '', '')
        dc.ui.log.v.line_log_summary.setFocus()

    @logger('NxLog.onDeleteLogClicked(self)', 'self')
    def onDeleteLogClicked(self):

        lid = dc.x.log.slid.v

        # are you sure? dialog
        t = 'Delete log?'
        q = 'Sure you want to delete log {}: {}?'\
                .format(str(lid), dc.sp.log._(lid).summary.v)
        yes, no = QMessageBox.Yes, QMessageBox.No
        response = QMessageBox.question(dc.ui.project.v, t, q, yes|no)
        if response == QMessageBox.StandardButton.No:
            return

        # remove log
        dc.sp.log.index.v.remove(lid)
        del dc.sp.log.__dict__['_{}'.format(lid)]
        dc.x.log.slid.v = 0

        # state
        loglist.reloadTable()
        dc.m.project.v.touchProject()

    # addAutoLog is the programatic interface to add log messages to the log
    # module. It is used by this class for user log creation as well as the
    # other gui control classes (project, roadmap) to add log messages.
    #
    # usage: dc.m.log.v.addAutoLog('Track', 'Project created',
    #                              'Project foo has been created')
    #
    # logtype can be 'User', 'Track' or 'Milestone'

    @logger('NxLog.addAutoLog(self, logtype, summary, message)',
            'self', 'logtype', 'summary', 'message')
    def addAutoLog(self, logtype, summary, message):

        timestamp = int(time.time())

        lid = dc.x.log.slid.v = dc.sp.nextlid.v
        dc.sp.log.index.v.add(lid)
        dc.sp.nextlid.v += 1

        dc.sp.log._(lid).created.v     = timestamp
        dc.sp.log._(lid).modified.v    = timestamp
        dc.sp.log._(lid).ltype.v       = logtype
        dc.sp.log._(lid).summary.v     = summary
        dc.sp.log._(lid).description.v = message

        loglist.reloadTable()
        dc.m.project.v.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

