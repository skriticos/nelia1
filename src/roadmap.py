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
    'box_selected_milestone': {'enabled': False}
}

states.selected = {
    'btn_mi_delete': {'enabled': True},
    'btn_mi_close': {'enabled': True},
    'box_selected_milestone': {'enabled': True}
}

dc.m.roadmap.states.v = states

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

'''
class Ef*(FocusOut)|*

dc.m.roadmap.ef.*.v = Ef*()
'''

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

        dc.m.log.v.addAutoLog('Milestone', 'Milestone item created',
                              'A new milestone item has been created')

        # update view

        milist.reloadTable()

        # STUB -> update milestone navi button

        applyStates(states.selected, dc.ui.roadmap.v)
        self.touchRoadmap()
        dc.ui.roadmap.v.line_mi_name.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


"""
import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton
from datacore import *
from common import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxRoadmapStates:

    @logger('NxRoadmapStates.enableAllCallbacks()')
    def enableAllCallbacks():

        # navi callbacks
        w = dc.ui.roadmap.v
        w.btn_show_logs             .clicked.connect(NxRoadmapStates.onShowLogs)
        w.btn_show_project          .clicked.connect(NxRoadmapStates.onShowProject)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Called when view changes to roadmap.
    # 1. Check if pid changed since last state --(no)--> return
    # 2. reload table
    # 3. set state

    @logger('NxRoadmapStates.onShown()')
    def onShown():
        log('STUB NxRoadmapStates.onShown()')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # switch to log and project views

    @logger('NxProjectStates.onShowLogs()')
    def onShowLogs():
        dc.ui.roadmap.v.setParent(dc.m.mainwindow.v)
        dc.m.log.states.v.onShown()
        dc.ui.main.v.setCentralWidget(dc.ui.log.v)

    @logger('NxProjectStates.onShowProject()')
    def onShowProject():
        dc.ui.roadmap.v.setParent(dc.m.mainwindow.v)
        dc.ui.main.v.setCentralWidget(dc.ui.project.v)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
filters = [
    'feature', 'issue', 'open', 'closed', 'low', 'medium', 'high',
    'core', 'auxiliary', 'security', 'corrective', 'architecture', 'refactor']
headers = [
    'ID', 'Name', 'Type', 'Status', 'Category', 'Priority',
    'Created', 'Modified']
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxRoadmap:

    @logger('NxRoadmap.__init__(self)', 'self')
    def __init__(self):

        dc.m.roadmap.v = self
        dc.m.roadmap.states.v = NxRoadmapStates

        NxRoadmapStates.enableAllCallbacks()

'''

        self.init = True
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.table = dc.ui.roadmap.v.table
        self.table.setModel(self.model)
        selmod = self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        win = dc.ui.roadmap.v
        win.push_add_feature.clicked.connect(self.onAddFeatureClicked)
        win.push_add_issue.clicked.connect(self.onAddIssueClicked)
        dc.ui.roadmap_diag_add.v.accepted.connect(self.onSubmitNewMI)
        dc.ui.roadmap_diag_edit.v.accepted.connect(self.onSubmitEditMI)
        win.push_delete.clicked.connect(self.onDeleteMIClicked)
        win.push_edit.clicked.connect(self.onEditMIClicked)
        win.push_close.clicked.connect(self.onCloseMIClicked)
        win.push_reopen.clicked.connect(self.onReopenMIClicked)
        dfin = dc.ui.roadmap_diag_finalize.v
        dfin.push_finalize_major.clicked.connect(self.onCloseMajorMs)
        dfin.push_finalize_minor.clicked.connect(self.onCloseMinorMs)
        selmod.selectionChanged.connect(self.onItemSelectionChanged)
        win.text_m_description.textChanged.connect(self.onMsDescChanged)
        self.table.activated.connect(self.onMIActivated)
        for w in ['label_selected', 'push_edit', 'push_delete', 'push_close',
                  'push_reopen']:
            dc.ui.roadmap.v.__dict__[w].hide()
        if dc.x.config.loaded.v:
            self.loadLayout()
        for f in filters:
            widget = win.__dict__['check_{}'.format(f)]
            widget.stateChanged.connect(self.reloadTable)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onShowTab(self)', 'self')
    def onShowTab(self):
        if dc.r.roadmap.pid.last.v == dc.spid.v: return
        dc.r.roadmap.pid.last.v = dc.spid.v
        self.smiid = 0
        dc.ui.roadmap.v.line_project.setText(dc.sp.name.v)
        dc.ui.roadmap_diag_add.v.line_project.setText(dc.sp.name.v)
        dc.ui.roadmap_diag_edit.v.line_project.setText(dc.sp.name.v)
        self.smajor, self.sminor = dc.sp.curr.major.v, dc.sp.curr.minor.v
        description = dc.sp.m._(self.smajor)._(self.sminor).description.v
        dc.ui.roadmap.v.text_m_description.setPlainText(description)
        self.updateRootMPushButton()
        self.reloadTable()
        d = dc.ui.roadmap_diag_add.v
        d.radio_medium.setChecked(True)
        d.radio_feature.setChecked(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onAddFeatureClicked(self)', 'self')
    def onAddFeatureClicked(self):
        dc.ui.roadmap_diag_add.v.radio_feature.setChecked(True)
        dc.ui.roadmap_diag_add.v.line_name.clear()
        dc.ui.roadmap_diag_add.v.text_description.clear()
        self.updateDiagMPushButton()
        dc.ui.roadmap_diag_add.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onAddIssueClicked(self)', 'self')
    def onAddIssueClicked(self):
        dc.ui.roadmap_diag_add.v.radio_issue.setChecked(True)
        dc.ui.roadmap_diag_add.v.line_name.clear()
        dc.ui.roadmap_diag_add.v.text_description.clear()
        self.updateDiagMPushButton()
        dc.ui.roadmap_diag_add.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onEditMIClicked(self)', 'self')
    def onEditMIClicked(self):
        diag = dc.ui.roadmap_diag_edit.v
        node = dc.sp.mi._(self.smiid)
        if node.itype.v == 'Feature': diag.radio_feature.setChecked(True)
        if node.itype.v == 'Issue':   diag.radio_issue.setChecked(True)
        itype, prio, cat = node.itype.v, node.priority.v, node.category.v
        if itype == 'Feature': diag.radio_feature.setChecked(True)
        if itype == 'Issue':   diag.radio_issue.setChecked(True)
        if prio == 'Low':    diag.radio_low.setChecked(True)
        if prio == 'Medium': diag.radio_medium.setChecked(True)
        if prio == 'High':   diag.radio_high.setChecked(True)
        if cat == 'Core':         diag.radio_core.setChecked(True)
        if cat == 'Auxiliary':    diag.radio_auxiliary.setChecked(True)
        if cat == 'Security':     diag.radio_security.setChecked(True)
        if cat == 'Corrective':   diag.radio_corrective.setChecked(True)
        if cat == 'Architecture': diag.radio_architecture.setChecked(True)
        if cat == 'Refactor':     diag.radio_refactor.setChecked(True)
        diag.line_name.setText(node.name.v)
        diag.text_description.setPlainText(node.description.v)
        self.updateDiagMPushButton()
        diag.show()
        diag.line_name.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onMIActivated(self)', 'self')
    def onMIActivated(self):
        cma, cmi = dc.sp.curr.major.v, dc.sp.curr.minor.v
        if self.smajor > cma or (self.smajor == cma and self.sminor >= cmi):
            self.onEditMIClicked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onSubmitNewMI(self)', 'self')
    def onSubmitNewMI(self):
        diag = dc.ui.roadmap_diag_add.v
        if diag.radio_feature.isChecked(): itype = 'Feature'
        if diag.radio_issue.isChecked():   itype = 'Issue'
        if diag.radio_medium.isChecked(): priority = 'Medium'
        elif diag.radio_high.isChecked(): priority = 'High'
        elif diag.radio_low.isChecked():  priority = 'Low'
        if diag.radio_core.isChecked():           category = 'Core'
        elif diag.radio_auxiliary.isChecked():    category = 'Auxiliary'
        elif diag.radio_security.isChecked():     category = 'Security'
        elif diag.radio_corrective.isChecked():   category = 'Corrective'
        elif diag.radio_architecture.isChecked(): category = 'Architecture'
        elif diag.radio_refactor.isChecked():     category = 'Refactor'
        tlabel = diag.push_target.text()
        major, minor = tlabel.split(' ')[3][1:].split('.')
        major, minor = int(major), int(minor)
        self.smiid = dc.sp.nextmiid.v
        dc.sp.nextmiid.v += 1
        dc.sp.midx.v[self.smiid] = major, minor
        node = dc.sp.mi._(self.smiid)
        node.name.v        = diag.line_name.text()
        node.description.v = diag.text_description.toPlainText()
        node.priority.v    = priority
        node.category.v    = category
        node.itype.v       = itype
        node.status.v      = 'Open'
        node.created.v     = node.modified.v = int(time.time())
        dc.sp.m._(major)._(minor).idx.v.add(self.smiid)
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onSubmitEditMI(self)', 'self')
    def onSubmitEditMI(self):
        diag = dc.ui.roadmap_diag_edit.v
        if diag.radio_feature.isChecked(): itype = 'Feature'
        if diag.radio_issue.isChecked():   itype = 'Issue'
        if diag.radio_medium.isChecked(): priority = 'Medium'
        elif diag.radio_high.isChecked(): priority = 'High'
        elif diag.radio_low.isChecked():  priority = 'Low'
        if diag.radio_core.isChecked():           category = 'Core'
        elif diag.radio_auxiliary.isChecked():    category = 'Auxiliary'
        elif diag.radio_security.isChecked():     category = 'Security'
        elif diag.radio_corrective.isChecked():   category = 'Corrective'
        elif diag.radio_architecture.isChecked(): category = 'Architecture'
        elif diag.radio_refactor.isChecked():     category = 'Refactor'
        tlabel = diag.push_target.text()
        major, minor = tlabel.split(' ')[3][1:].split('.')
        major, minor = int(major), int(minor)
        if (major, minor) != dc.sp.midx.v[self.smiid]:
            old_major, old_minor = dc.sp.midx.v[self.smiid]
            if len(dc.sp.m._(old_major)._(old_minor).idx.v) != 1:
                dc.sp.m._(old_major)._(old_minor).idx.v.remove(self.smiid)
                dc.sp.m._(major)._(minor).idx.v.add(self.smiid)
                dc.sp.midx.v[self.smiid] = major, minor
            else:
                m = 'Can\'t move last milestone item!'
                QMessageBox.critical(dc.ui.roadmap.v, m, m)
        node = dc.sp.mi._(self.smiid)
        node.itype.v       = itype
        node.name.v        = diag.line_name.text()
        node.category.v    = category
        node.priority.v    = priority
        node.description.v = diag.text_description.toPlainText()
        node.changed.v     = int(time.time())
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onDeleteMIClicked(self)', 'self')
    def onDeleteMIClicked(self):
        del dc.sp.mi.__dict__['_{}'.format(self.smiid)]
        major, minor = dc.sp.midx.v[self.smiid]
        del dc.sp.midx.v[self.smiid]
        dc.sp.m._(major)._(minor).idx.v.remove(self.smiid)
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onItemSelectionChanged(self, item_selection, previous)',
            'self', 'item_selection', 'previous')
    def onItemSelectionChanged(self, item_selection, previous):
        indexes = item_selection.indexes()
        if not indexes:
            if not len(dc.sp.m._(self.smajor)._(self.sminor).idx.v):
                for w in ['label_selected', 'push_edit', 'push_delete',
                          'push_close', 'push_reopen']:
                    dc.ui.roadmap.v.__dict__[w].hide()
            return
        for w in ['label_selected', 'push_edit', 'push_delete']:
            dc.ui.roadmap.v.__dict__[w].show()
        row = indexes[0].row()
        index = self.model.index(row, 0)
        item  = self.model.itemFromIndex(index)
        self.smiid = int(item.text())
        description = dc.sp.mi._(self.smiid).description.v
        self.init = True
        dc.ui.roadmap.v.text_mi_description.setPlainText(description)
        self.init = False
        if dc.sp.mi._(self.smiid).status.v == 'Open':
            dc.ui.roadmap.v.push_close.show()
            dc.ui.roadmap.v.push_reopen.hide()
        if dc.sp.mi._(self.smiid).status.v == 'Closed':
            dc.ui.roadmap.v.push_close.hide()
            dc.ui.roadmap.v.push_reopen.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onCloseMinorMs(self)', 'self')
    def onCloseMinorMs(self):
        dc.sp.mi._(self.smiid).status.v = 'Closed'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        dc.sp.curr.minor.v += 1
        self.sminor += 1
        self.reloadTable()
        self.updateRootMPushButton()
        dc.ui.roadmap_diag_finalize.v.hide()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onCloseMajorMs(self)', 'self')
    def onCloseMajorMs(self):
        dc.sp.mi._(self.smiid).status.v = 'Closed'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        x = max(dc.sp.m._(self.smajor).idx.v)
        dc.sp.m._(self.smajor).idx.v.remove(x)
        dc.sp.curr.major.v += 1
        dc.sp.curr.minor.v = 0
        self.sminor = 0
        self.smajor = dc.sp.curr.major.v
        self.reloadTable()
        self.updateRootMPushButton()
        dc.ui.roadmap_diag_finalize.v.hide()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onMsDescChanged(self)', 'self')
    def onMsDescChanged(self):
        if self.init: return
        description = dc.ui.roadmap.v.text_m_description.toPlainText()
        dc.sp.m._(self.smajor)._(self.sminor).description.v = description
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onCloseMIClicked(self)', 'self')
    def onCloseMIClicked(self):
        sumopen = 0
        ma, mi = self.smajor, self.sminor
        if ma == dc.sp.curr.major.v and mi == dc.sp.curr.minor.v:
            for itemid in dc.sp.m._(ma)._(mi).idx.v:
                if dc.sp.mi._(itemid).status.v == 'Open': sumopen += 1
            if sumopen == 1:
                self.closeMs()
            else:
                dc.sp.mi._(self.smiid).status.v = 'Closed'
                dc.sp.mi._(self.smiid).changed.v = int(time.time())
                dc.m.project.v.touchProject()
                self.reloadTable()
        self.updateRootMPushButton()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onReopenMIClicked(self)', 'self')
    def onReopenMIClicked(self):
        dc.sp.mi._(self.smiid).status.v = 'Open'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        dc.m.project.v.touchProject()
        self.reloadTable()
        self.updateRootMPushButton()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.onRootMPushButtonChanged(self, major, minor)',
            'self', 'major', 'minor')
    def onRootMPushButtonChanged(self, major, minor):
        self.smajor = major
        self.sminor = minor
        description = dc.sp.m._(major)._(minor).description.v
        dc.ui.roadmap.v.text_m_description.setPlainText(description)
        self.updateRootMPushButton()
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.updateMsTree(self)', 'self')
    def updateMsTree(self):
        for major in reversed(list(dc.sp.m.idx.v)):
            major_index = dc.sp.m.idx
            loop_major = dc.sp.m._(major)
            if major > 1:
                previous_major_has_item \
                        = bool(len(dc.sp.m._(major-1)._(0).idx.v))
                if not previous_major_has_item:
                    major_index.v.remove(major)
                    del dc.sp.m.__dict__['_{}'.format(major)]
                    continue
            if major > 0:
                next_major_exists = major+1 in major_index.v
                has_item = bool(len(loop_major._(0).idx.v))
                if has_item and not next_major_exists:
                    major_index.v.add(major+1)
                    next_major = dc.sp.m._(major+1)
                    next_major.idx.v = {0}
                    next_major._(0).description.v = ''
                    next_major._(0).idx.v = set()
                    loop_major.idx.v.add(1)
                    loop_major._(1).description.v = ''
                    loop_major._(1).idx.v = set()
                    continue
            lastminor = max(loop_major.idx.v)
            last_minor_has_item = bool(len(loop_major._(lastminor).idx.v))
            if last_minor_has_item:
                loop_major.idx.v.add(lastminor+1)
                loop_major._(lastminor+1).description.v = ''
                loop_major._(lastminor+1).idx.v = set()
            if major == 0 and lastminor == 1: continue
            if lastminor == 0: continue
            has_multiple_minors = False
            if major == 0 and lastminor > 1:
                has_multiple_minors = True
            if major > 0 and lastminor > 0:
                has_multiple_minors = True
            previous_to_last_minor_has_item \
                    = bool(len(loop_major._(lastminor-1).idx.v))
            if has_multiple_minors and not previous_to_last_minor_has_item:
                loop_major.idx.v.remove(lastminor)
                del loop_major.__dict__['_{}'.format(lastminor)]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.closeMs(self)', 'self')
    def closeMs(self):
        sumopen = 0
        for itemid in dc.sp.m._(self.smajor)._(self.sminor+1).idx.v:
            if dc.sp.mi._(itemid).status.v == 'Open': sumopen += 1
        diag = dc.ui.roadmap_diag_finalize.v
        if sumopen: diag.push_finalize_major.setEnabled(False)
        else:       diag.push_finalize_major.setEnabled(True)
        diag.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.saveLayout(self)', 'self')
    def saveLayout(self):
        dc.c.roadmap.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.roadmap.header.width.v.append(self.table.columnWidth(i))
        cnode   = dc.c.roadmap.sort.column
        cnode.v = self.horizontal_header.sortIndicatorSection()
        cnode   = dc.c.roadmap.sort.order
        cnode.v = self.horizontal_header.sortIndicatorOrder().__repr__()
        for f in filters:
            cnode   = dc.c.roadmap._('show_{}'.format(f))
            cnode.v = dc.ui.roadmap.v.__dict__['check_{}'.format(f)].isChecked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.loadLayout(self)', 'self')
    def loadLayout(self):
        for index, width in enumerate(dc.c.roadmap.header.width.v):
            self.table.setColumnWidth(index, width)
        if dc.c.roadmap.sort.column.v:
            column = dc.c.roadmap.sort.column.v
            order  = convert(dc.c.roadmap.sort.order.v)
            self.horizontal_header.setSortIndicator(column, order)
        for f in filters:
            widget = dc.ui.roadmap.v.__dict__['check_{}'.format(f)]
            widget.setChecked(dc.c.roadmap._('show_{}'.format(f)).v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.reloadTable(self)', 'self')
    def reloadTable(self, state=None):
        if not dc.ui.roadmap.v.isVisible():
            return
        self.init = True
        self.saveLayout()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        dc.ui.roadmap.v.push_close.setText('&Close Item')
        self.smajor, self.sminor = dc.ui.roadmap.v.push_milestone.getVersion()
        filter_status = set()
        for name in filters:
            if dc.ui.roadmap.v.__dict__['check_'+name].isChecked():
                filter_status.add(name)
        for miid in dc.sp.m._(self.smajor)._(self.sminor).idx.v:
            md = dc.sp.mi._(miid)
            if {md.itype.v.lower(), md.status.v.lower(),
                    md.category.v.lower(), md.priority.v.lower()} \
                   .issubset(filter_status):
                self.model.insertRow(0, [
                    QStandardItem(str(miid).zfill(4)),
                    QStandardItem(md.name.v),
                    QStandardItem(md.itype.v),
                    QStandardItem(md.status.v),
                    QStandardItem(md.category.v),
                    QStandardItem(md.priority.v),
                    QStandardItem(convert(md.created.v)),
                    QStandardItem(convert(md.modified.v)) ])
        self.init = False
        if self.model.rowCount(): self.table.selectRow(0)
        self.loadLayout()
        self.table.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.updateRootMPushButton(self)', 'self')
    def updateRootMPushButton(self):
        ui = dc.ui.roadmap.v
        ui.gridLayout_3.removeWidget(ui.push_milestone)
        ui.push_milestone.hide()
        ui.push_milestone.close()
        ma, mi = self.smajor, self.sminor
        ui.push_milestone = MPushButton(ui, ma, mi)
        ui.push_milestone.change_signal.connect(self.onRootMPushButtonChanged)
        ui.gridLayout_3.addWidget(ui.push_milestone, 0, 1, 1, 1)
        ui.label_2.setBuddy(ui.push_milestone)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxRoadmap.updateDiagMPushButton(self)', 'self')
    def updateDiagMPushButton(self):
        diags = dc.ui.roadmap_diag_add.v, dc.ui.roadmap_diag_edit.v
        for d in diags:
            d.gridLayout_2.removeWidget(d.push_target)
            d.push_target.close()
            d.push_target = MPushButton(d, self.smajor, self.sminor, True)
            d.gridLayout_2.addWidget(d.push_target, 1, 1, 1, 1);
            d.label_3.setBuddy(d.push_target)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
"""
