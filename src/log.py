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

    dc.states.log.maximized.v = state
    dc.m.log.v.updateStates('onLogMaxToggled')

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
        dc.states.log.selected.userlog.v = False
        dc.states.log.selected.applog.v = False
        dc.m.log.v.updateStates('onSelectionChanged')
        return

    # get selected lid from table model
    index = indexes[0]
    slid = int(dc.x.log.model.v.itemFromIndex(index).text())

    dc.x.log.slid.v = slid

    # populate edit fields on selection change
    disableEditCallbacks()
    dc.ui.log.v.lbl_log_type.setText(dc.sp.log._(slid).ltype.v)
    dc.ui.log.v.lbl_log_created.setText(convert(dc.sp.log._(slid).created.v))
    dc.ui.log.v.lbl_log_modified.setText(convert(dc.sp.log._(slid).modified.v))
    dc.ui.log.v.line_log_summary.setText(dc.sp.log._(slid).summary.v)
    dc.ui.log.v.text_log_message.setText(dc.sp.log._(slid).description.v)
    enableEditCallbacks()

    row = index.row()

    if row != dc.x.log.row.v:

        dc.x.log.row.v = row

    if dc.sp.log._(slid).ltype.v == 'User':

        dc.states.log.selected.userlog.v = True
        dc.states.log.selected.applog.v = False

    else:

        dc.states.log.selected.userlog.v = False
        dc.states.log.selected.applog.v = True

    dc.m.log.v.updateStates('onSelectionChanged')

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

    dc.ui.log.v.tbl_log_list.setFocus()

    saveLayout('log')

    autoprev = dc.auto.v
    dc.auto.v = True
    disableSelectionCallback()
    dc.x.log.model.v.clear()
    dc.x.log.selection_model.v.reset()
    enableSelectionCallback()
    dc.x.log.model.v.setHorizontalHeaderLabels(loglist.headers)
    dc.auto.v = False

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

        dc.states.log.startup.v = True

    # we don't have a selected log id (outside the filter or deleted)
    elif not dc.x.log.slid.v:

        index = dc.x.log.model.v.index(0, 0)
        lid   = int(dc.x.log.model.v.data(index))
        dc.x.log.slid.v = lid

        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.log.selection_model.v.setCurrentIndex(index, s|r)
        selection = dc.x.log.view.v.selectionModel().selection()

    else:

        # iterate through table rows
        for rowcnt in range(dc.x.log.model.v.rowCount()):

            index = dc.x.log.model.v.index(rowcnt, 0)
            lid = int(dc.x.log.model.v.data(index))

            # if we have a match, select it and abort
            if lid == dc.x.log.slid.v:

                s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                dc.x.log.selection_model.v.setCurrentIndex(index, s|r)
                selection = dc.x.log.view.v.selectionModel().selection()
                break

    dc.m.log.v.updateStates('reloadTable')

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

        dc.states.log.focustable.v          = False
        dc.states.log.maximized.v           = False
        dc.states.log.newuserlog.v          = False
        dc.states.log.noupdate.v            = False
        dc.states.log.selected.applog.v	    = False
        dc.states.log.selected.userlog.v	= False
        dc.states.log.startup.v	            = True

        self.updateStates('NxLog.__init__')

        loglist.initTable()
        enableAllCallbacks()

        dc.x.log.changeflag.log_description.v = False
        dc.ui.log.v.text_log_message.installEventFilter(ef_log_desription_focus_out)

    @logger('NxRoadmap.initNavi(self)', 'self')
    def initNavi(self):

        dc.ui.log.v.btn_show_roadmap.clicked.connect(dc.m.roadmap.v.onShow)
        dc.ui.log.v.btn_show_project.clicked.connect(dc.m.project.v.onShow)

    @logger('NxLog.onShow(self)', 'self')
    def onShow(self):

        dc.ui.project.v.setParent(None)
        dc.ui.roadmap.v.setParent(None)
        dc.ui.main.v.setCentralWidget(dc.ui.log.v)

        if dc.x.lpid.v != dc.spid.v:
            dc.x.lpid.v = dc.spid.v

            dc.ui.log.v.lbl_project_name.setText(dc.sp.name.v)
            loglist.reloadTable()

    @logger('NxLog.updateStates(self, source)', 'self', 'source')
    def updateStates(self, source):

        if dc.states.log.noupdate.v:

            return

        if dc.states.log.focustable.v:

            dc.states.log.focustable.v = False

            applyStates({
                'tbl_log_list': {'focused': True}}, dc.ui.log.v)

        if dc.states.log.startup.v:

            dc.states.log.startup.v = False

            applyStates({
                'btn_log_maximize': {'enabled': False},
                'btn_log_new':      {'enabled': True, 'focused': True},
                'btn_log_delete':   {'enabled': False},
                'btn_show_project': {'enabled': True},
                'btn_show_roadmap': {'enabled': True},
                'log_meta':         {'visible': True},
                'line_log_summary': {'enabled': False, 'clear': True},
                'text_log_message': {'enabled': False, 'clear': True},
                'lbl_log_type':     {'clear': True},
                'lbl_log_created':  {'clear': True},
                'lbl_log_modified': {'clear': True},
                'group_log_list':   {'visible': True}}, dc.ui.log.v)

            return

        if dc.states.log.newuserlog.v:

            dc.states.log.newuserlog.v = False

            applyStates({
                'btn_log_maximize': {'enabled': True},
                'btn_log_new':      {'enabled': True},
                'btn_log_delete':   {'enabled': True},
                'btn_show_project': {'enabled': True},
                'btn_show_roadmap': {'enabled': True},
                'log_meta':         {'visible': True},
                'line_log_summary': {'enabled': True, 'clear': True},
                'text_log_message': {'enabled': True, 'clear': True},
                'group_log_list':   {'visible': True}}, dc.ui.log.v)

            return

        if dc.states.log.maximized.v:

            applyStates({
                'btn_log_maximize': {'enabled': True},
                'btn_log_new':      {'enabled': False},
                'btn_log_delete':   {'enabled': False},
                'btn_show_project': {'enabled': False},
                'btn_show_roadmap': {'enabled': False},
                'log_meta':         {'visible': False},
                'line_log_summary': {'enabled': True},
                'text_log_message': {'enabled': True},
                'group_log_list':   {'visible': False}}, dc.ui.log.v)

            return

        if dc.states.log.selected.userlog.v:

            applyStates({
                'btn_log_maximize': {'enabled': True},
                'btn_log_new':      {'enabled': True},
                'btn_log_delete':   {'enabled': True},
                'btn_show_project': {'enabled': True},
                'btn_show_roadmap': {'enabled': True},
                'log_meta':         {'visible': True},
                'line_log_summary': {'enabled': True},
                'text_log_message': {'enabled': True},
                'group_log_list':   {'visible': True}}, dc.ui.log.v)

            return

        if dc.states.log.selected.applog.v:

            applyStates({
                'btn_log_maximize': {'enabled': True},
                'btn_log_new':      {'enabled': True},
                'btn_log_delete':   {'enabled': True},
                'btn_show_project': {'enabled': True},
                'btn_show_roadmap': {'enabled': True},
                'log_meta':         {'visible': True},
                'line_log_summary': {'enabled': False},
                'text_log_message': {'enabled': False},
                'group_log_list':   {'visible': True}}, dc.ui.log.v)

            return

    @logger('NxLog.touchLog(self)', 'self')
    def touchLog(self):

        timestamp = int(time.time())
        lid = dc.x.log.slid.v
        dc.sp.log._(lid).modified.v = timestamp
        x = convert(timestamp)
        setTableValue('log', loglist.colModified, x)
        dc.ui.log.v.lbl_log_modified.setText(x)
        dc.m.project.v.touchProject('log.touchLog')

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

        dc.states.log.newuserlog.v = True
        self.updateStates('onNewLogClicked')
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
        if not dc.sp.log.index.v:
            dc.states.log.startup.v = True
        self.updateStates('onDeleteLogClicked')
        dc.m.project.v.touchProject('log.onDeleteLogClicked')

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

        dc.m.project.v.touchProject('log.addAutoLog')
        loglist.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

