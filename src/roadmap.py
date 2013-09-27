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

import mistctrl                       # milestone control module for new project
from mistnavi import MilestoneButton

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

    dc.ui.roadmap.v.btn_milestone_button.selectionChanged.connect(onMilestoneSelectionChanged)

    dc.ui.finalize.v.btn_abort.clicked.connect(onFinalizeAbort)
    dc.ui.finalize.v.btn_finminor.clicked.connect(dc.m.roadmap.v.onMinorMilestoneFinalized)
    dc.ui.finalize.v.btn_finmajor.clicked.connect(dc.m.roadmap.v.onMajorMilestoneFinalized)

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
    dc.ui.roadmap.v.text_milestone_description.textChanged.connect(
        dc.m.roadmap.v.onMilestoneDescriptionChanged)
    dc.ui.roadmap.v.txt_mi_description.textChanged.connect(
        dc.m.roadmap.v.onMilestoneItemDestriptionChanged)

@logger('(roadmap) disableEditCallbacks()')
def disableEditCallbacks():

    dc.ui.roadmap.v.line_mi_name.textChanged.disconnect(dc.m.roadmap.v.onNameChanged)
    dc.ui.roadmap.v.cb_mi_priority.currentIndexChanged[str].connect(dc.m.roadmap.v.onPriorityChanged)
    dc.ui.roadmap.v.cb_mi_category.currentIndexChanged[str].connect(dc.m.roadmap.v.onCategoryChanged)
    dc.ui.roadmap.v.cb_mi_type.currentIndexChanged[str].disconnect(dc.m.roadmap.v.onTypeChanged)
    dc.ui.roadmap.v.text_milestone_description.textChanged.disconnect(
        dc.m.roadmap.v.onMilestoneDescriptionChanged)
    dc.ui.roadmap.v.txt_mi_description.textChanged.disconnect(
        dc.m.roadmap.v.onMilestoneItemDestriptionChanged)

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

@logger('(roadmap) onMilestoneSelectionChanged(x=None)')
def onMilestoneSelectionChanged(x=None):

    smajor, sminor = dc.sp.m.selected.v
    amajor, aminor = dc.sp.m.active.v
    if smajor < amajor or (smajor == amajor and sminor < aminor):
        dc.states.roadmap.selected.finalized.v = True
    else:
        dc.states.roadmap.selected.none_.v = True
    dc.m.roadmap.v.updateStates('onMilestoneSelectionChanged')

    dc.m.roadmap.milist.v.reloadTable()

    autoprev = dc.auto.v
    dc.auto.v = True
    major, minor = dc.sp.m.selected.v
    dc.ui.roadmap.v.text_milestone_description.setHtml(
        dc.sp.m._(major)._(minor).description.v)
    dc.auto.v = autoprev

@logger('(roadmap) onFilterFeatureToggled(checked)', 'checked')
def onFilterFeatureToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Feature')
    else:
        dc.c.roadmap.filters.v.discard('Feature')
    milist.reloadTable()

@logger('(roadmap) onFilterIssueToggled(checked)', 'checked')
def onFilterIssueToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Issue')
    else:
        dc.c.roadmap.filters.v.discard('Issue')
    milist.reloadTable()

@logger('(roadmap) onFilterOpenToggled(checked)', 'checked')
def onFilterOpenToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Open')
    else:
        dc.c.roadmap.filters.v.discard('Open')
    milist.reloadTable()

@logger('(roadmap) onFilterClosedToggled(checked)', 'checked')
def onFilterClosedToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Closed')
    else:
        dc.c.roadmap.filters.v.discard('Closed')
    milist.reloadTable()

@logger('(roadmap) onFilterLowToggled(checked)', 'checked')
def onFilterLowToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Low')
    else:
        dc.c.roadmap.filters.v.discard('Low')
    milist.reloadTable()

@logger('(roadmap) onFilterMediumToggled(checked)', 'checked')
def onFilterMediumToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Medium')
    else:
        dc.c.roadmap.filters.v.discard('Medium')
    milist.reloadTable()

@logger('(roadmap) onFilterHighToggled(checked)', 'checked')
def onFilterHighToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('High')
    else:
        dc.c.roadmap.filters.v.discard('High')
    milist.reloadTable()

@logger('(roadmap) onFilterCoreToggled(checked)', 'checked')
def onFilterCoreToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Core')
    else:
        dc.c.roadmap.filters.v.discard('Core')
    milist.reloadTable()

@logger('(roadmap) onFilterAuxiliaryToggled(checked)', 'checked')
def onFilterAuxiliaryToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Auxiliary')
    else:
        dc.c.roadmap.filters.v.discard('Auxiliary')
    milist.reloadTable()

@logger('(roadmap) onFilterSecurityToggled(checked)', 'checked')
def onFilterSecurityToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Security')
    else:
        dc.c.roadmap.filters.v.discard('Security')
    milist.reloadTable()

@logger('(roadmap) onFilterCorrectiveToggled(checked)', 'checked')
def onFilterCorrectiveToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Corrective')
    else:
        dc.c.roadmap.filters.v.discard('Corrective')
    milist.reloadTable()

@logger('(roadmap) onFilterArchitectureToggled(checked)', 'checked')
def onFilterArchitectureToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Architecture')
    else:
        dc.c.roadmap.filters.v.discard('Architecture')
    milist.reloadTable()

@logger('(roadmap) onFilterRefactorToggled(checked)', 'checked')
def onFilterRefactorToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.roadmap.filters.v.add('Refactor')
    else:
        dc.c.roadmap.filters.v.discard('Refactor')
    milist.reloadTable()

@logger('(roadmap) onMaximizeMilestoneDescription(setMaximized)', 'setMaximized')
def onMaximizeMilestoneDescription(setMaximized):

    if setMaximized:
        dc.states.roadmap.maxmilestonedesc.v = setMaximized
    else:
        dc.states.roadmap.unmaximized.v = True

    dc.m.roadmap.v.updateStates('onMaximizeMilestoneDescription')

@logger('(roadmap) onMaximizeMilestoneItemDescription(setMaximized)', 'setMaximized')
def onMaximizeMilestoneItemDescription(setMaximized):

    if setMaximized:
        dc.states.roadmap.maxmidesc.v = setMaximized
    else:
        dc.states.roadmap.unmaximized.v = True

    dc.m.roadmap.v.updateStates('onMaximizeMilestoneItemDescription')

@logger('(roadmap) onSelectionChanged()')
def onSelectionChanged(new, old):

    # check for valid index
    indexes = new.indexes()
    if not indexes:

        dc.states.roadmap.startup.v = True
        dc.m.roadmap.v.updateStates('onSelectionChanged')
        return

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

    row = index.row()
    if row != dc.x.roadmap.row.v:
        dc.x.roadmap.row.v = row

    smajor, sminor = dc.sp.m.selected.v
    amajor, aminor = dc.sp.m.active.v
    if smajor < amajor or (smajor == amajor and sminor < aminor):
        dc.states.roadmap.selected.finalized.v = True
    elif smajor > amajor or (smajor == amajor and sminor > aminor):
        dc.states.roadmap.selected.future.v = True
    elif dc.sp.m.mi._(smiid).status.v == 'Closed':
        dc.states.roadmap.selected.closed.v = True
    else:
        dc.states.roadmap.selected.open_.v = True

    dc.m.roadmap.v.updateStates('onSelectionChanged')

@logger('(roadmap) onFinalizeAbort()')
def onFinalizeAbort():

    dc.ui.finalize.v.hide()
    dc.ui.roadmap.v.gridLayout_4.removeWidget(
        dc.ui.finalize.v)
    dc.ui.roadmap.v.gridLayout_4.addWidget(
        dc.ui.roadmap.v.body, 1, 0)
    dc.ui.roadmap.v.body.show()

    dc.states.roadmap.selected.open_.v = True
    dc.m.roadmap.v.updateStates('onFinalizeAbort')

CbAux.onSelectionChanged    = onSelectionChanged

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

CbAux.onFinalizeAbort = onFinalizeAbort

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

@logger('milist.initRoadmapFilterControls()')
def initRoadmapFilterControls():

    # restore table sorting and headers
    loadLayout('roadmap')

    if 'Feature' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_feature.setChecked(True)
    if 'Issue' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_issue.setChecked(True)
    if 'Open' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_open.setChecked(True)
    if 'Closed' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_closed.setChecked(True)
    if 'Low' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_low.setChecked(True)
    if 'Medium' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_medium.setChecked(True)
    if 'High' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_high.setChecked(True)
    if 'Core' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_core.setChecked(True)
    if 'Auxiliary' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_auxiliary.setChecked(True)
    if 'Security' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_security.setChecked(True)
    if 'Corrective' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_corrective.setChecked(True)
    if 'Architecture' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_architecture.setChecked(True)
    if 'Refactor' in dc.c.roadmap.filters.v:
        dc.ui.roadmap.v.btn_filter_refactor.setChecked(True)

@logger('milist.reloadTable()')
def reloadTable():

    dc.ui.roadmap.v.tbl_mi_list.setFocus()

    saveLayout('roadmap')

    autoprev = dc.auto.v
    dc.auto.v = True
    disableSelectionCallback()
    dc.x.roadmap.model.v.clear()
    dc.x.roadmap.selection_model.v.reset()
    dc.x.roadmap.model.v.setHorizontalHeaderLabels(milist.headers)
    enableSelectionCallback()
    dc.auto.v = autoprev

    major, minor = dc.sp.m.selected.v
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
    if dc.x.roadmap.smiid.v not in dc.sp.m._(major)._(minor).index.v:
        dc.x.roadmap.smiid.v = None

    # we don't select anything if we don't have rows
    rowcount = dc.x.roadmap.model.v.rowCount()
    if rowcount <= 0:

        dc.x.roadmap.row.v = -1

        smajor, sminor = dc.sp.m.selected.v
        amajor, aminor = dc.sp.m.active.v
        if smajor < amajor or (smajor == amajor and sminor < aminor):
            dc.states.roadmap.selected.nonefin.v = True
        else:
            dc.states.roadmap.selected.none_.v = True


    # we don't have a selected milestone item id (outside the filter or deleted)
    elif not dc.x.roadmap.smiid.v:

        index = dc.x.roadmap.model.v.index(0, 0)
        smiid = dc.x.roadmap.smiid.v = int(dc.x.roadmap.model.v.data(index))

        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.roadmap.selection_model.v.setCurrentIndex(index, s|r)
        selection = dc.x.roadmap.view.v.selectionModel().selection()

        return

    else:

        # iterate through table rows
        for rowcnt in range(dc.x.roadmap.model.v.rowCount()):

            index = dc.x.roadmap.model.v.index(rowcnt, 0)
            miid = int(dc.x.roadmap.model.v.data(index))

            # if we have a match, select it and abort
            if miid == dc.x.roadmap.smiid.v:

                smiid = miid
                s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                dc.x.roadmap.selection_model.v.setCurrentIndex(index, s|r)
                selection = dc.x.roadmap.view.v.selectionModel().selection()

                break

    dc.m.roadmap.v.updateStates('reloadTable')

milist.initTable = initTable
milist.initRoadmapFilterControls = initRoadmapFilterControls
milist.reloadTable = reloadTable
dc.m.roadmap.milist.v = milist

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

class EfMilestoneDescriptionFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.milestone_description.v:
                description = dc.ui.roadmap.v.text_milestone_description.toHtml()
                major, minor = dc.sp.m.selected.v
                dc.sp.m._(major)._(minor).description.v = description
            dc.x.roadmap.changeflag.milestone_description.v = False
        return QObject.eventFilter(self, obj, event)
ef_milestone_desription_focus_out = EfMilestoneDescriptionFocusOut()

class EfMilestoneItemDescriptionFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.roadmap.changeflag.milestone_item_description.v:
                description = dc.ui.roadmap.v.txt_mi_description.toHtml()
                smiid = dc.x.roadmap.smiid.v
                dc.sp.m.mi._(smiid).description.v = description
            dc.x.roadmap.changeflag.milestone_item_description.v = False
        return QObject.eventFilter(self, obj, event)
ef_milestone_item_desription_focus_out = EfMilestoneItemDescriptionFocusOut()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxRoadmap:

    @logger('NxRoadmap.__init__(self)', 'self')
    def __init__(self):

        dc.m.roadmap.v = self
        milist.initTable()

        dc.ui.roadmap.v.btn_milestone_button.close()
        btn = dc.ui.roadmap.v.btn_milestone_button \
            = MilestoneButton(dc.ui.roadmap.v.box_milestone_selection)
        dc.ui.roadmap.v.layout_mi_select.addWidget(btn, 0, 1, 1, 1)

        initCallbacks()

        if not isinstance(dc.c.roadmap.filters.v, set):
            dc.c.roadmap.filters.v = {
                'Feature', 'Issue', 'Open', 'Low', 'Medium', 'High', 'Core',
                'Auxiliary', 'Security', 'Corrective', 'Architecture',
                'Refactor'
            }

        dc.x.roadmap.changeflag.name.v = False
        dc.x.roadmap.changeflag.mtype.v = False
        dc.x.roadmap.changeflag.priority.v = False
        dc.x.roadmap.changeflag.category.v = False
        dc.x.roadmap.changeflag.milestone_description.v = False
        dc.x.roadmap.changeflag.milestone_item_description.v = False

        dc.states.roadmap.dialog.v	            = False
        dc.states.roadmap.focustable.v	        = False
        dc.states.roadmap.maxmidesc.v	        = False
        dc.states.roadmap.maxmilestonedesc.v    = False
        dc.states.roadmap.newmi.v	            = False
        dc.states.roadmap.noupdate.v	        = False
        dc.states.roadmap.selected.closed.v	    = False
        dc.states.roadmap.selected.finalized.v	= False
        dc.states.roadmap.selected.future.v	    = False
        dc.states.roadmap.selected.open_.v	    = False
        dc.states.roadmap.selected.none_.v	    = False
        dc.states.roadmap.unmaximized.v         = False
        dc.states.roadmap.startup.v	            = True
        self.updateStates('__init__')

        dc.ui.roadmap.v.line_mi_name.installEventFilter(ef_name_focus_out)
        dc.ui.roadmap.v.cb_mi_type.installEventFilter(ef_type_focus_out)
        dc.ui.roadmap.v.cb_mi_priority.installEventFilter(ef_priority_focus_out)
        dc.ui.roadmap.v.cb_mi_category.installEventFilter(ef_category_focus_out)
        dc.ui.roadmap.v.text_milestone_description.installEventFilter(
            ef_milestone_desription_focus_out)
        dc.ui.roadmap.v.txt_mi_description.installEventFilter(
            ef_milestone_item_desription_focus_out)

    @logger('NxRoadmap.initNavi(self)', 'self')
    def initNavi(self):

        dc.ui.roadmap.v.btn_show_project.clicked.connect(dc.m.project.v.onShow)
        dc.ui.roadmap.v.btn_show_logs.clicked.connect(dc.m.log.v.onShow)

    @logger('NxRoadmap.onShow(self)', 'self')
    def onShow(self):

        dc.ui.project.v.setParent(None)
        dc.ui.log.v.setParent(None)
        dc.ui.main.v.setCentralWidget(dc.ui.roadmap.v)

        if dc.x.rpid.v != dc.spid.v:
            dc.x.rpid.v = dc.spid.v

            dc.ui.roadmap.v.lbl_project_name.setText(dc.sp.name.v)
            dc.ui.roadmap.v.btn_milestone_button.updateMenuTree()
            onMilestoneSelectionChanged('')
            milist.reloadTable()

    @logger('NxRoadmap.updateStates(self, source)', 'self', 'source')
    def updateStates(self, source):

        if dc.states.roadmap.noupdate.v:

            return

        if dc.states.roadmap.focustable.v:

            applyStates({
                'tbl_mi_list': {'focused': True}}, dc.ui.roadmap.v)

        if dc.states.roadmap.startup.v:

            dc.states.roadmap.startup.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': False},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': False, 'clear': True},
                'cb_mi_type':           {'enabled': False, 'index': 0},
                'cb_mi_priority':       {'enabled': False, 'index': 0},
                'cb_mi_category':       {'enabled': False, 'index': 0},
                'text_milestone_description':
                                        {'iswritable': True, 'clear': True},
                'txt_mi_description':   {'iswritable': False, 'clear': True}},
                dc.ui.roadmap.v)

            return

        if dc.states.roadmap.newmi.v:

            dc.states.roadmap.newmi.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': True},
                'btn_mi_close':         {'enabled': True},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': True, 'clear': True},
                'cb_mi_type':           {'enabled': True, 'index': 0},
                'cb_mi_priority':       {'enabled': True, 'index': 0},
                'cb_mi_category':       {'enabled': True, 'index': 0},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {'iswritable': True, 'clear': True}},
                dc.ui.roadmap.v)

            return

        if dc.states.roadmap.maxmilestonedesc.v:

            dc.states.roadmap.maxmilestonedesc.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': False},
                'btn_show_project':     {'enabled': False},
                'btn_show_logs':        {'enabled': False},
                'btn_mi_new':           {'enabled': False},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': False},
                'group_mi_list':        {'visible': False},
                'line_mi_name':         {},
                'cb_mi_type':           {},
                'cb_mi_priority':       {},
                'cb_mi_category':       {},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.maxmidesc.v:

            dc.states.roadmap.maxmidesc.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': False},
                'btn_show_project':     {'enabled': False},
                'btn_show_logs':        {'enabled': False},
                'btn_mi_new':           {'enabled': False},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': False},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': False},
                'line_mi_name':         {},
                'cb_mi_type':           {},
                'cb_mi_priority':       {},
                'cb_mi_category':       {},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.unmaximized.v:

            dc.states.roadmap.unmaximized.v = False

            smajor, sminor = dc.sp.m.selected.v
            amajor, aminor = dc.sp.m.active.v

            if smajor < amajor or (smajor == amajor and sminor < aminor):
                dc.states.roadmap.selected.finalized.v = True
            elif smajor > amajor or (smajor == amajor and sminor > aminor):
                dc.states.roadmap.selected.future.v = True
            elif not dc.x.roadmap.smiid.v:
                dc.states.roadmap.selected.none_.v = True
            elif dc.sp.m.mi._(dc.x.roadmap.smiid.x).status.v == 'Closed':
                dc.states.roadmap.selected.closed.v = True
            else:
                dc.states.roadmap.selected.open_.v = True

            self.updateStates('updateStates')

            return

        if dc.states.roadmap.selected.open_.v:

            dc.states.roadmap.selected.open_.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': True},
                'btn_mi_close':         {'enabled': True},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': True},
                'cb_mi_type':           {'enabled': True},
                'cb_mi_priority':       {'enabled': True},
                'cb_mi_category':       {'enabled': True},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {'iswritable': True}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.selected.closed.v:

            dc.states.roadmap.selected.closed.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': True},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': True},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': False},
                'cb_mi_type':           {'enabled': False},
                'cb_mi_priority':       {'enabled': False},
                'cb_mi_category':       {'enabled': False},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {'iswritable': False}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.selected.none_.v:

            dc.states.roadmap.selected.none_.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': False},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': False, 'clear': True},
                'cb_mi_type':           {'enabled': False, 'index': 0},
                'cb_mi_priority':       {'enabled': False, 'index': 0},
                'cb_mi_category':       {'enabled': False, 'index': 0},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {'iswritable': False, 'clear': True}},
                dc.ui.roadmap.v)

            return

        if dc.states.roadmap.selected.nonefin.v:

            dc.states.roadmap.selected.nonefin.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': False},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': False, 'clear': True},
                'cb_mi_type':           {'enabled': False, 'index': 0},
                'cb_mi_priority':       {'enabled': False, 'index': 0},
                'cb_mi_category':       {'enabled': False, 'index': 0},
                'text_milestone_description':
                                        {'iswritable': False},
                'txt_mi_description':   {'iswritable': False, 'clear': True}},
                dc.ui.roadmap.v)

            return

        if dc.states.roadmap.selected.finalized.v:

            dc.states.roadmap.selected.finalized.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': False},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': False},
                'cb_mi_type':           {'enabled': False},
                'cb_mi_priority':       {'enabled': False},
                'cb_mi_category':       {'enabled': False},
                'text_milestone_description':
                                        {'iswritable': False},
                'txt_mi_description':   {'iswritable': False}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.selected.future.v:

            dc.states.roadmap.selected.future.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': True},
                'btn_milestone_button': {'enabled': True},
                'btn_show_project':     {'enabled': True},
                'btn_show_logs':        {'enabled': True},
                'btn_mi_new':           {'enabled': True},
                'btn_mi_delete':        {'enabled': True},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description':
                                        {'visible': True},
                'group_selected_milestone':
                                        {'visible': True},
                'group_mi_list':        {'visible': True},
                'line_mi_name':         {'iswritable': True},
                'cb_mi_type':           {'enabled': True},
                'cb_mi_priority':       {'enabled': True},
                'cb_mi_category':       {'enabled': True},
                'text_milestone_description':
                                        {'iswritable': True},
                'txt_mi_description':   {'iswritable': True}}, dc.ui.roadmap.v)

            return

        if dc.states.roadmap.dialog.v:

            dc.states.roadmap.dialog.v = False

            applyStates({
                'btn_mi_desc_minimize': {'enabled': False},
                'btn_milestone_button': {'enabled': False},
                'btn_show_project':     {'enabled': False},
                'btn_show_logs':        {'enabled': False},
                'btn_mi_new':           {'enabled': False},
                'btn_mi_delete':        {'enabled': False},
                'btn_mi_close':         {'enabled': False},
                'btn_mi_reopen':        {'enabled': False},
                'group_milestone_description': {},
                'group_selected_milestone': {},
                'group_mi_list':        {},
                'line_mi_name':         {},
                'cb_mi_type':           {},
                'cb_mi_priority':       {},
                'cb_mi_category':       {},
                'text_milestone_description': {},
                'txt_mi_description':   {}}, dc.ui.roadmap.v)

            return

    @logger('NxRoadmap.onMilestoneDescriptionChanged(self)', 'self')
    def onMilestoneDescriptionChanged(self):

        self.touchRoadmap()

        if not dc.auto.v:
            dc.x.roadmap.changeflag.milestone_description.v = True

    @logger('NxRoadmap.touchRoadmap(self)', 'self')
    def touchRoadmap(self):

        if dc.auto.v:
            return

        timestamp = int(time.time())
        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).modified.v = timestamp
        x = convert(timestamp)
        setTableValue('roadmap', milist.colModified, x)
        dc.m.project.v.touchProject('roadmap.touchRoadmap')

    @logger('NxRoadmap.onNameChanged(self, name)', 'self', 'name')
    def onNameChanged(self, name):

        if not dc.auto.v:
            smiid = dc.x.roadmap.smiid.v
            dc.sp.m.mi._(smiid).name.v = name
            setTableValue('roadmap', milist.colName, name)
            self.touchRoadmap()
            dc.x.roadmap.changeflag.name.v = True

    @logger('NxRoadmap.onPriorityChanged(self, priority)', 'self', 'priority')
    def onPriorityChanged(self, priority):

        if not dc.auto.v:
            smiid = dc.x.roadmap.smiid.v
            dc.sp.m.mi._(smiid).priority.v = priority
            setTableValue('roadmap', milist.colPriority, priority)
            self.touchRoadmap()
            dc.x.roadmap.changeflag.priority.v = True

    @logger('NxRoadmap.onCategoryChanged(self, category)', 'self', 'category')
    def onCategoryChanged(self, category):

        if not dc.auto.v:
            smiid = dc.x.roadmap.smiid.v
            dc.sp.m.mi._(smiid).category.v = category
            setTableValue('roadmap', milist.colCategory, category)
            self.touchRoadmap()
            dc.x.roadmap.changeflag.category.v = True

    @logger('NxRodamap.onTypeChange(self, v\mtype)', 'self', 'mtype')
    def onTypeChanged(self, mtype):

        if not dc.auto.v:
            smiid = dc.x.roadmap.smiid.v
            dc.sp.m.mi._(smiid).mtype.v = mtype
            setTableValue('roadmap', milist.colType, mtype)
            self.touchRoadmap()

            # update milestone navi button
            major, minor = dc.sp.m.selected.v
            dc.ui.roadmap.v.btn_milestone_button.updateMajorMilestone(major)

            dc.x.roadmap.changeflag.mtype.v = True

        # STUB: notify mistctrl about milestone tree change

    @logger('NxRoadmap.onMilestoneItemDestriptionChanged(self)', 'self')
    def onMilestoneItemDestriptionChanged(self):

            if not dc.auto.v:
                self.touchRoadmap()
                dc.x.roadmap.changeflag.milestone_item_description.v = True

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

        # update milestone navi button
        mistctrl.calibrateRoadmapMi()
        dc.ui.roadmap.v.btn_milestone_button.updateMajorMilestone(major)
        self.touchRoadmap()
        dc.ui.roadmap.v.line_mi_name.setFocus()

    @logger('NxRoadmap.onMiClosed(self)', 'self')
    def onMiClosed(self):

        if dc.sp.m.active.v != dc.sp.m.selected.v:
            raise Exception('control states are invalid or active / selected'
                            'milestone tracking is corrupted')

        major, minor = dc.sp.m.active.v
        opencnt = 0
        for miid in dc.sp.m._(major)._(minor).index.v:

            if dc.sp.m.mi._(miid).status.v == 'Open':
                opencnt += 1

        # closing last item
        if opencnt == 1:

            dc.states.roadmap.dialog.v = True
            self.updateStates('onMiClosed')

            # show finalize dialog
            dc.ui.roadmap.v.body.hide()
            dc.ui.roadmap.v.gridLayout_4.removeWidget(
                dc.ui.roadmap.v.body)
            dc.ui.roadmap.v.gridLayout_4.addWidget(
                dc.ui.finalize.v, 1, 0)
            dc.ui.finalize.v.show()

            dc.ui.finalize.v.btn_finminor.setFocus()
            nextminor = minor + 1
            if len(dc.sp.m._(major)._(nextminor).index.v) == 0:
                dc.ui.finalize.v.btn_finmajor.setEnabled(True)
            else:
                dc.ui.finalize.v.btn_finmajor.setEnabled(False)
            return

        # close milestones item
        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Closed'
        setTableValue('roadmap', milist.colStatus, 'Closed')
        self.touchRoadmap()
        logMiEvent('closed', 'item has been closed')
        milist.reloadTable()
        # update milestone navi button
        major, minor = dc.sp.m.selected.v
        dc.ui.roadmap.v.btn_milestone_button.updateMajorMilestone(major)

    @logger('NxRoadmap.onMiReopen(self)', 'self')
    def onMiReopen(self):

        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Open'
        setTableValue('roadmap', milist.colStatus, 'Open')
        self.touchRoadmap()
        milist.reloadTable()

        logMiEvent('reopened', 'item has been reopned')

        # update milestone navi button
        major, minor = dc.sp.m.selected.v
        dc.ui.roadmap.v.btn_milestone_button.updateMajorMilestone(major)

    @logger('NxRoadmap.onDeleteMilestoneItem(self)', 'self')
    def onDeleteMilestoneItem(self):

        smiid = dc.x.roadmap.smiid.v

        logMiEvent('deleted', 'item has been deleted')

        major, minor = dc.sp.m.selected.v
        dc.sp.m._(major)._(minor).index.v.discard(smiid)
        del dc.sp.m.mi.__dict__['_{}'.format(smiid)]
        dc.m.project.v.touchProject('roadmap.onDeleteMilestoneItem')
        dc.x.roadmap.smiid.v = 0
        milist.reloadTable()

        # update milestone navi button
        major, minor = dc.sp.m.selected.v
        mistctrl.calibrateRoadmapMi()
        dc.ui.roadmap.v.btn_milestone_button.updateMajorMilestone(major)

    @logger('NxRoadmap.onMinorMilestoneFinalized(self)', 'self')
    def onMinorMilestoneFinalized(self):

        # we start with finisching milestone item closing that was started
        # before the dialgo appeared. This is the same as the last part of
        # onMiClosed. We just leave out the table reload, as the following
        # milestone selection switch will take care of that.
        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Closed'
        self.touchRoadmap()
        logMiEvent('closed', 'item has been closed')

        amajor, aminor = dc.sp.m.active.v
        dc.m.log.v.addAutoLog('Milestone', 'Minor milestone finalized',
                  'Minor milestone {}.{} finalized.'.format(amajor, aminor))

        # calibrate roadmap tree
        mistctrl.calibrateMinorMsClosed()

        # hide finalize dialog
        dc.ui.finalize.v.hide()
        dc.ui.roadmap.v.gridLayout_4.removeWidget(
            dc.ui.finalize.v)
        dc.ui.roadmap.v.gridLayout_4.addWidget(
            dc.ui.roadmap.v.body, 1, 0)
        dc.ui.roadmap.v.body.show()

        dc.states.roadmap.startup.v = True
        self.updateStates('onMinorMilestoneFinalized')

        dc.ui.roadmap.v.btn_milestone_button.updateMenuTree()
        milist.reloadTable()

    @logger('NxRoadmap.onMajorMilestoneFinalized(self)', 'self')
    def onMajorMilestoneFinalized(self):

        # we start with finisching milestone item closing that was started
        # before the dialog appeared. This is the same as the last part of
        # onMiClosed. We just leave out the table reload, as the following
        # milestone selection switch will take care of that.
        smiid = dc.x.roadmap.smiid.v
        dc.sp.m.mi._(smiid).status.v = 'Closed'
        self.touchRoadmap()
        logMiEvent('closed', 'item has been closed')

        amajor, aminor = dc.sp.m.active.v
        dc.m.log.v.addAutoLog('Milestone', 'Major milestone finalized',
                  'Major milestone {} finalized.'.format(amajor))

        # calibrate roadmap tree
        mistctrl.calibrateMajorMsClosed()

        # hide finalize dialog
        dc.ui.finalize.v.hide()
        dc.ui.roadmap.v.gridLayout_4.removeWidget(dc.ui.finalize.v)
        dc.ui.roadmap.v.gridLayout_4.addWidget(dc.ui.roadmap.v.body, 1, 0)
        dc.ui.roadmap.v.body.show()

        dc.states.roadmap.startup.v = True
        self.updateStates('onMajorMilestoneFinalized')

        dc.ui.roadmap.v.btn_milestone_button.updateMenuTree()
        milist.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

