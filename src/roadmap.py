# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file contains the roadmap module core. It manages the roadmap widget
# controls, milestone item display and changes.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import datetime
import time

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from datacore import *
from common import *
from common2 import *

# might want to bring these two modules into this source file?
import mistctrl                       # milestone control module for new project
import mistnavi                       # milestone navigation button

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# STATES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class states: pass

states.startup = {
    'btn_mi_delete': {'enabled': False},
    'btn_mi_close':  {'enabled': False},
    'btn_mi_reopen': {'enabled': False},
    'group_selected_milestone': {'enabled': False}
}

states.selected = {
    'btn_mi_delete': {'enabled': True},
    'btn_mi_close': {'enabled': True},
    'group_selected_milestone': {'enabled': True}
}

states.miopen = {
    'btn_mi_close' : {'enabled': True},
    'btn_mi_reopen': {'enabled': False}
}

states.miclosed = {
    'btn_mi_close' : {'enabled': False},
    'btn_mi_reopen': {'enabled': True}
}

states.milestone_description_maximized = {
    'group_log_list': {'visible': False},
    'group_selected_milestone': {'visible': False},
    'text_milestone_description': {'focused': None}
}

states.selected_milestone_item_description_maximized = {
    'group_log_list': {'visible': False},
    'group_milestone_description': {'visible': False},
    'group_edit_attr': {'visible': False},
    'txt_mi_description': {'focused': None}
}

states.all_unmaximized = {
    'group_log_list': {'visible': True},
    'group_selected_milestone': {'visible': True},
    'group_milestone_description': {'visible': True},
    'group_edit_attr': {'visible': True},
    'tbl_mi_list': {'focused': None}
}

dc.m.roadmap.states.v = states

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY FUNCTIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class FnAux: pass

@logger('(roadmap) logMiEvent(summary, detail)', 'summary', 'detail')
def logMiEvent(summary, detail):

    smiid = dc.x.roadmap.smiid.v
    name = dc.sp.m.mi._(smiid).name.v
    major = dc.sp.m.selected.v[0]
    minor = dc.sp.m.selected.v[1]

    if summary == 'created':
        dc.m.log.v.addAutoLog('Milestone',
                              'Milestone item {} {}'.format(smiid, summary),
                              'Milestone item {}: {}'.format(smiid, detail))
    else:
        dc.m.log.v.addAutoLog('Milestone',
                              'Milestone item {} {}'.format(smiid, summary),
                              'Milestone item {} - "{}": {}'.format(smiid, name, detail))

FnAux.logMiEvent = logMiEvent
dc.m.roadmap.fnaux.v = FnAux

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALLBACK CONTROL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Functions to enable / disable callback groups.
# External example: dc.m.roadmap.cbctrl.v.initCallbacks()
# Internal example: initCallbacks() or CbCtrl.initCallbacks()

class CbCtrl: pass

@logger('(roadmap) initCallbacks()')
def initCallbacks():

    # loads allways on callbacks
    dc.ui.roadmap.v.btn_show_project.clicked.connect(onShowProject)
    dc.ui.roadmap.v.btn_show_logs.clicked.connect(onShowLogs)
    dc.ui.roadmap.v.btn_mi_new.clicked.connect(dc.m.roadmap.v.onNewMilestoneItem)
    dc.ui.roadmap.v.btn_mi_close.clicked.connect(dc.m.roadmap.v.onMiClosed)
    dc.ui.roadmap.v.btn_mi_reopen.clicked.connect(dc.m.roadmap.v.onMiReopen)
    dc.ui.roadmap.v.btn_mi_delete.clicked.connect(dc.m.roadmap.v.onDeleteMilestoneItem)

    dc.ui.roadmap.v.btn_filter_feature.toggled.connect(onFilterFeatureToggled)
    dc.ui.roadmap.v.btn_filter_issue.toggled.connect(onFilterIssueToggled)
    dc.ui.roadmap.v.btn_filter_open.toggled.connect(onFilterOpenToggled)
    dc.ui.roadmap.v.btn_filter_closed.toggled.connect(onFilterClosedToggled)
    dc.ui.roadmap.v.btn_filter_low.toggled.connect(onFilterLowToggled)
    dc.ui.roadmap.v.btn_filter_medium.toggled.connect(onFilterMediumToggled)
    dc.ui.roadmap.v.btn_filter_high.toggled.connect(onFilterHighToggled)
    dc.ui.roadmap.v.btn_filter_core.toggled.connect(onFilterCoreToggled)
    dc.ui.roadmap.v.btn_filter_auxiliary.toggled.connect(onFilterAuxiliaryToggled)
    dc.ui.roadmap.v.btn_filter_security.toggled.connect(onFilterSecurityToggled)
    dc.ui.roadmap.v.btn_filter_corrective.toggled.connect(onFilterCorrectiveToggled)
    dc.ui.roadmap.v.btn_filter_architecture.toggled.connect(onFilterArchitectureToggled)
    dc.ui.roadmap.v.btn_filter_refactor.toggled.connect(onFilterRefactorToggled)

    dc.ui.roadmap.v.btn_milestone_maximize.toggled.connect(onMaximizeMilestoneDescription)
    dc.ui.roadmap.v.btn_mi_desc_minimize.toggled.connect(onMaximizeMilestoneItemDescription)

    enableSelectionCallback()
    enableEditCallbacks()

@logger('(roadmap) enableSelectionCallback()')
def enableSelectionCallback():

    dc.x.roadmap.selection_model.v.selectionChanged.connect(onSelectionChanged)

@logger('(roadmap) disableSelectionCallback()')
def disableSelectionCallback():

    dc.x.roadmap.selection_model.v.selectionChanged.disconnect(onSelectionChanged)

@logger('(roadmap) enableEditCallbacks()')
def enableEditCallbacks():

    dc.ui.roadmap.v.line_mi_name.textChanged.connect(dc.m.roadmap.v.onNameChanged)
    dc.ui.roadmap.v.cb_mi_priority.currentIndexChanged[str].connect(dc.m.roadmap.v.onPriorityChanged)
    dc.ui.roadmap.v.cb_mi_category.currentIndexChanged[str].connect(dc.m.roadmap.v.onCategoryChanged)
    dc.ui.roadmap.v.cb_mi_type.currentIndexChanged[str].connect(dc.m.roadmap.v.onTypeChanged)

@logger('(roadmap) disableEditCallbacks()')
def disableEditCallbacks():

    dc.ui.roadmap.v.line_mi_name.textChanged.disconnect(dc.m.roadmap.v.onNameChanged)
    dc.ui.roadmap.v.cb_mi_priority.currentIndexChanged[str].connect(dc.m.roadmap.v.onPriorityChanged)
    dc.ui.roadmap.v.cb_mi_category.currentIndexChanged[str].connect(dc.m.roadmap.v.onCategoryChanged)
    dc.ui.roadmap.v.cb_mi_type.currentIndexChanged[str].disconnect(dc.m.roadmap.v.onTypeChanged)

CbCtrl.initCallbacks            = initCallbacks
CbCtrl.enableSelectionCallback  = enableSelectionCallback
CbCtrl.disableSelectionCallback = disableSelectionCallback
CbCtrl.enableEditCallbacks      = enableEditCallbacks
CbCtrl.disableEditCallbacks     = disableEditCallbacks

dc.m.roadmap.cbctrl.v = CbCtrl

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY CALLBACK IMPLEMENTATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Auxiliary callback functions
# External example: dc.m.roadmap.cbaux.v.onShow()
# Internal example: onShow() or CbAux.onShow()

class CbAux: pass

@logger('(roadmap) onFilterFeatureToggled(checked)', 'checked')
def onFilterFeatureToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Feature')
    else:
        dc.c.roadmap.filters.v.discard('Feature')
    milist.reloadTable()

@logger('(roadmap) onFilterIssueToggled(checked)', 'checked')
def onFilterIssueToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Issue')
    else:
        dc.c.roadmap.filters.v.discard('Issue')
    milist.reloadTable()

@logger('(roadmap) onFilterOpenToggled(checked)', 'checked')
def onFilterOpenToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Open')
    else:
        dc.c.roadmap.filters.v.discard('Open')
    milist.reloadTable()

@logger('(roadmap) onFilterClosedToggled(checked)', 'checked')
def onFilterClosedToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Closed')
    else:
        dc.c.roadmap.filters.v.discard('Closed')
    milist.reloadTable()

@logger('(roadmap) onFilterLowToggled(checked)', 'checked')
def onFilterLowToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Low')
    else:
        dc.c.roadmap.filters.v.discard('Low')
    milist.reloadTable()

@logger('(roadmap) onFilterMediumToggled(checked)', 'checked')
def onFilterMediumToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Medium')
    else:
        dc.c.roadmap.filters.v.discard('Medium')
    milist.reloadTable()

@logger('(roadmap) onFilterHighToggled(checked)', 'checked')
def onFilterHighToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('High')
    else:
        dc.c.roadmap.filters.v.discard('High')
    milist.reloadTable()

@logger('(roadmap) onFilterCoreToggled(checked)', 'checked')
def onFilterCoreToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Core')
    else:
        dc.c.roadmap.filters.v.discard('Core')
    milist.reloadTable()

@logger('(roadmap) onFilterAuxiliaryToggled(checked)', 'checked')
def onFilterAuxiliaryToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Auxiliary')
    else:
        dc.c.roadmap.filters.v.discard('Auxiliary')
    milist.reloadTable()

@logger('(roadmap) onFilterSecurityToggled(checked)', 'checked')
def onFilterSecurityToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Security')
    else:
        dc.c.roadmap.filters.v.discard('Security')
    milist.reloadTable()

@logger('(roadmap) onFilterCorrectiveToggled(checked)', 'checked')
def onFilterCorrectiveToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Corrective')
    else:
        dc.c.roadmap.filters.v.discard('Corrective')
    milist.reloadTable()

@logger('(roadmap) onFilterArchitectureToggled(checked)', 'checked')
def onFilterArchitectureToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Architecture')
    else:
        dc.c.roadmap.filters.v.discard('Architecture')
    milist.reloadTable()

@logger('(roadmap) onFilterRefactorToggled(checked)', 'checked')
def onFilterRefactorToggled(checked):

    if checked:
        dc.c.roadmap.filters.v.add('Refactor')
    else:
        dc.c.roadmap.filters.v.discard('Refactor')
    milist.reloadTable()

@logger('(roadmap) onMaximizeMilestoneDescription(setMaximized)', 'setMaximized')
def onMaximizeMilestoneDescription(setMaximized):

    if setMaximized:
        applyStates(states.milestone_description_maximized, dc.ui.roadmap.v)
    else:
        applyStates(states.all_unmaximized, dc.ui.roadmap.v)

@logger('(roadmap) onMaximizeMilestoneItemDescription(setMaximized)', 'setMaximized')
def onMaximizeMilestoneItemDescription(setMaximized):

    if setMaximized:
        applyStates(states.selected_milestone_item_description_maximized, dc.ui.roadmap.v)
    else:
        applyStates(states.all_unmaximized, dc.ui.roadmap.v)

@logger('(roadmap) onSelectionChanged()')
def onSelectionChanged(new, old):

    auto_prev = dc.auto.v
    dc.auto.v = True

    # check for valid index
    indexes = new.indexes()
    if indexes:

        # get selected lid from table model

        index = indexes[0]
        smiid = dc.x.roadmap.smiid.v \
             = int(dc.x.roadmap.model.v.itemFromIndex(index).text())

        # populate edit fields on selection change

        disableEditCallbacks()

        ui = dc.ui.roadmap.v
        ui.line_mi_name.setText(dc.sp.m.mi._(smiid).name.v)
        ui.cb_mi_type.setCurrentIndex(
                ui.cb_mi_type.findText(dc.sp.m.mi._(smiid).mtype.v))
        ui.cb_mi_priority.setCurrentIndex(
                ui.cb_mi_priority.findText(dc.sp.m.mi._(smiid).priority.v))
        ui.cb_mi_category.setCurrentIndex(
                ui.cb_mi_category.findText(dc.sp.m.mi._(smiid).category.v))
        ui.txt_mi_description.setText(dc.sp.m.mi._(smiid).description.v)

        enableEditCallbacks()

        if dc.sp.m.mi._(smiid).status.v == 'Open':
            applyStates(states.miopen, dc.ui.roadmap.v)
        else:
            applyStates(states.miclosed, dc.ui.roadmap.v)

    dc.auto.v = auto_prev

@logger('(roadmap) onShowLogs()')
def onShowLogs():
    dc.ui.roadmap.v.setParent(None)
    dc.m.log.onShown.v()
    dc.ui.main.v.setCentralWidget(dc.ui.log.v)

@logger('(roadmap) onShowProject()')
def onShowProject():

    dc.ui.roadmap.v.setParent(None)
    dc.ui.log.v.setParent(dc.m.mainwindow.v)
    dc.ui.main.v.setCentralWidget(dc.ui.project.v)

@logger('(roadmap) onShow()')
def onShow():

    dc.ui.roadmap.v.lbl_project_name.setText(dc.sp.name.v)

CbAux.onSelectionChanged    = onSelectionChanged
CbAux.onShow                = onShow
CbAux.onShowLogs            = onShowLogs
CbAux.onShowProject         = onShowProject

CbAux.onFilterFeatureToggled        = onFilterFeatureToggled
CbAux.onFilterIssueToggled          = onFilterIssueToggled
CbAux.onFilterOpenToggled           = onFilterOpenToggled
CbAux.onFilterClosedToggled         = onFilterClosedToggled
CbAux.onFilterLowToggled            = onFilterLowToggled
CbAux.onFilterMediumToggled         = onFilterMediumToggled
CbAux.onFilterHighToggled           = onFilterHighToggled
CbAux.onFilterCoreToggled           = onFilterCoreToggled
CbAux.onFilterAuxiliaryToggled      = onFilterAuxiliaryToggled
CbAux.onFilterSecurityToggled       = onFilterSecurityToggled
CbAux.onFilterCorrectiveToggled     = onFilterCorrectiveToggled
CbAux.onFilterArchitectureToggled   = onFilterArchitectureToggled
CbAux.onFilterRefactorToggled       = onFilterRefactorToggled

CbAux.onMaximizeMilestoneDescription = onMaximizeMilestoneDescription
CbAux.onMaximizeMilestoneItemDescription = onMaximizeMilestoneItemDescription

dc.m.roadmap.cbaux.v = CbAux

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class milist: pass

milist.headers = [
    'ID',
    'Name',
    'Status',
    'Type',
    'Priority',
    'Category',
    'Modified',
    'Created'
]

milist.colId        = 0
milist.colName      = 1
milist.colStatus    = 2
milist.colType      = 3
milist.colPriority  = 4
milist.colCategory  = 5
milist.colModified  = 6
milist.colCreated   = 7

@logger('milist.initTable()')
def initTable():

    view = dc.x.roadmap.view.v = dc.ui.roadmap.v.tbl_mi_list
    model = dc.x.roadmap.model.v = QStandardItemModel()
    view.setModel(model)
    model.setHorizontalHeaderLabels(milist.headers)
    dc.x.roadmap.selection_model.v = view.selectionModel()
    dc.x.roadmap.horizontal_header.v = view.horizontalHeader()

@logger('milist.reloadTable()')
def reloadTable():

    saveLayout('roadmap')

    disableSelectionCallback()
    dc.x.roadmap.model.v.clear()
    dc.x.roadmap.selection_model.v.reset()
    dc.x.roadmap.model.v.setHorizontalHeaderLabels(milist.headers)
    enableSelectionCallback()

    major, minor = dc.sp.m.active.v
    for miid in dc.sp.m._(major)._(minor).index.v:

        # check for filter status

        if (dc.sp.m.mi._(miid).mtype.v not in dc.c.roadmap.filters.v) or \
           (dc.sp.m.mi._(miid).status.v not in dc.c.roadmap.filters.v) or \
           (dc.sp.m.mi._(miid).priority.v not in dc.c.roadmap.filters.v) or \
           (dc.sp.m.mi._(miid).category.v not in dc.c.roadmap.filters.v):

            dc.x.roadmap.smiid.v = 0
            continue

        # add row to table
        dc.x.roadmap.model.v.insertRow(0, [
            QStandardItem(str(miid).zfill(4)),
            QStandardItem(dc.sp.m.mi._(miid).name.v),
            QStandardItem(dc.sp.m.mi._(miid).status.v),
            QStandardItem(dc.sp.m.mi._(miid).mtype.v),
            QStandardItem(dc.sp.m.mi._(miid).priority.v),
            QStandardItem(dc.sp.m.mi._(miid).category.v),
            QStandardItem(convert(dc.sp.m.mi._(miid).modified.v)),
            QStandardItem(convert(dc.sp.m.mi._(miid).created.v))
        ])

    loadLayout('roadmap')

    # select active milestone item

    # we don't select anything if we don't have rows
    rowcount = dc.x.roadmap.model.v.rowCount()
    if rowcount <= 0:

        applyStates(states.startup, dc.ui.roadmap.v)
        return

    # we don't have a selected milestone item id (outside the filter or deleted)
    if not dc.x.roadmap.smiid.v:

        index = dc.x.roadmap.model.v.index(0, 0)
        lid   = int(dc.x.roadmap.model.v.data(index))
        dc.x.roadmap.smiid.v = lid

        disableEditCallbacks()
        applyStates(states.selected, dc.ui.roadmap.v)
        enableEditCallbacks()

        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.roadmap.selection_model.v.setCurrentIndex(index, s|r)
        selection = dc.x.roadmap.view.v.selectionModel().selection()

        return

    # iterate through table rows
    for rowcnt in range(dc.x.roadmap.model.v.rowCount()):

        index = dc.x.roadmap.model.v.index(rowcnt, 0)
        lid = int(dc.x.roadmap.model.v.data(index))

        # if we have a match, select it and abort
        if lid == dc.x.roadmap.smiid.v:

            disableEditCallbacks()
            applyStates(states.selected, dc.ui.roadmap.v)
            enableEditCallbacks()

            s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
            dc.x.roadmap.selection_model.v.setCurrentIndex(index, s|r)
            selection = dc.x.roadmap.view.v.selectionModel().selection()
            break

milist.initTable = initTable
milist.reloadTable = reloadTable

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EVENT FILTERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class EfNameFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.name.v:
                logMiEvent('name changed', 'name changed to {}'.format(
                           dc.sp.m.mi._(dc.x.roadmap.smiid.v).name.v))
            dc.x.roadmap.changeflag.name.v = False
        return QObject.eventFilter(self, obj, event)
ef_name_focus_out = EfNameFocusOut()

class EfTypeFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.mtype.v:
                logMiEvent('type changed', 'type changed to {}'.format(
                           dc.sp.m.mi._(dc.x.roadmap.smiid.v).mtype.v))
            dc.x.roadmap.changeflag.mtype.v = False
        return QObject.eventFilter(self, obj, event)
ef_type_focus_out = EfTypeFocusOut()

class EfPriorityFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.priority.v:
                logMiEvent('priority changed', 'priority changed to {}'.format(
                           dc.sp.m.mi._(dc.x.roadmap.smiid.v).priority.v))
            dc.x.roadmap.changeflag.priority.v = False
        return QObject.eventFilter(self, obj, event)
ef_priority_focus_out = EfPriorityFocusOut()

class EfCategoryFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.category.v:
                logMiEvent('category changed', 'category changed to {}'.format(
                           dc.sp.m.mi._(dc.x.roadmap.smiid.v).category.v))
            dc.x.roadmap.changeflag.category.v = False
        return QObject.eventFilter(self, obj, event)
ef_category_focus_out = EfCategoryFocusOut()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxRoadmap:

    @logger('NxRoadmap.__init__(self)', 'self')
    def __init__(self):

        dc.m.roadmap.v = self
        applyStates(states.startup, dc.ui.roadmap.v)
        milist.initTable()
        initCallbacks()

        if not dc.c.roadmap.filters.v:
            dc.c.roadmap.filters.v = {
                'Feature', 'Issue', 'Open', 'Low', 'Medium', 'High', 'Core',
                'Auxiliary', 'Security', 'Corrective', 'Architecture',
                'Refactor'
            }

        dc.x.roadmap.changeflag.name.v = False
        dc.x.roadmap.changeflag.mtype.v = False
        dc.x.roadmap.changeflag.priority.v = False
        dc.x.roadmap.changeflag.category.v = False
        dc.ui.roadmap.v.line_mi_name.installEventFilter(ef_name_focus_out)
        dc.ui.roadmap.v.cb_mi_type.installEventFilter(ef_type_focus_out)
        dc.ui.roadmap.v.cb_mi_priority.installEventFilter(ef_priority_focus_out)
        dc.ui.roadmap.v.cb_mi_category.installEventFilter(ef_category_focus_out)

    @logger('NxRoadmap.touchRoadmap(self)', 'self')
    def touchRoadmap(self):

        timestamp = int(time.time())
        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).modified.v = timestamp
        x = convert(timestamp)
        setTableValue('roadmap', milist.colModified, x)
        dc.m.project.v.touchProject()

    @logger('NxRoadmap.onNameChanged(self, name)', 'self', 'name')
    def onNameChanged(self, name):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).name.v = name
        setTableValue('roadmap', milist.colName, name)
        self.touchRoadmap()

        if not dc.auto.v:
            dc.x.roadmap.changeflag.name.v = True

    @logger('NxRoadmap.onPriorityChanged(self, priority)', 'self', 'priority')
    def onPriorityChanged(self, priority):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).priority.v = priority
        setTableValue('roadmap', milist.colPriority, priority)
        self.touchRoadmap()

        if not dc.auto.v:
            dc.x.roadmap.changeflag.priority.v = True

    @logger('NxRoadmap.onCategoryChanged(self, category)', 'self', 'category')
    def onCategoryChanged(self, category):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).category.v = category
        setTableValue('roadmap', milist.colCategory, category)
        self.touchRoadmap()

        if not dc.auto.v:
            dc.x.roadmap.changeflag.category.v = True

    @logger('NxRodamap.onTypeChange(self, v\mtype)', 'self', 'mtype')
    def onTypeChanged(self, mtype):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).mtype.v = mtype
        setTableValue('roadmap', milist.colType, mtype)
        self.touchRoadmap()

        if not dc.auto.v:
            dc.x.roadmap.changeflag.mtype.v = True

        # STUB: notify mistctrl about milestone tree change

    @logger('NxRoadmap.onNewMilestoneItem(self)', 'self')
    def onNewMilestoneItem(self):

        timestamp = int(time.time())

        # get location and mark new milestone item as selected

        dc.x.roadmap.smiid.v = miid = dc.sp.m.mi.nextid.v
        dc.sp.m.mi.nextid.v += 1

        major, minor = dc.sp.m.selected.v

        # register new item

        dc.sp.m._(major)._(minor).index.v.add(miid)
        dc.sp.m.mi.index.v[miid] = (major, minor)

        # assign new milestone item values

        dc.sp.m.mi._(miid).name.v = ''
        dc.sp.m.mi._(miid).status.v = 'Open'
        dc.sp.m.mi._(miid).mtype.v = 'Feature'
        dc.sp.m.mi._(miid).priority.v = 'Medium'
        dc.sp.m.mi._(miid).category.v = 'Core'
        dc.sp.m.mi._(miid).description.v = ''
        dc.sp.m.mi._(miid).created.v = timestamp
        dc.sp.m.mi._(miid).modified.v = timestamp

        # log entry

        logMiEvent('created', 'item created')

        # update view

        milist.reloadTable()

        # STUB -> update milestone navi button

        applyStates(states.selected, dc.ui.roadmap.v)
        self.touchRoadmap()
        dc.ui.roadmap.v.line_mi_name.setFocus()

    @logger('NxRoadmap.onMiClosed(self)', 'self')
    def onMiClosed(self):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Closed'
        setTableValue('roadmap', milist.colStatus, 'Closed')
        self.touchRoadmap()
        milist.reloadTable()

        logMiEvent('closed', 'item has been closed')

        # STUB: update mistnavi

    @logger('NxRoadmap.onMiReopen(self)', 'self')
    def onMiReopen(self):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Open'
        setTableValue('roadmap', milist.colStatus, 'Open')
        self.touchRoadmap()
        milist.reloadTable()

        logMiEvent('reopened', 'item has been reopned')

        # STUB: update mistnavi

    @logger('NxRoadmap.onDeleteMilestoneItem(self)', 'self')
    def onDeleteMilestoneItem(self):

        smiid = dc.x.roadmap.smiid.v

        logMiEvent('deleted', 'item has been deleted')

        major, minor = dc.sp.m.selected.v
        dc.sp.m._(major)._(minor).index.v.discard(smiid)
        del dc.sp.m.mi.__dict__['_{}'.format(smiid)]
        dc.m.project.v.touchProject()
        dc.x.roadmap.smiid.v = 0
        milist.reloadTable()

        # STUB: update mistnavi

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

