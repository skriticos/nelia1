# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file contains the business end of the project widget. This manages the
# documents and the projects within the documents.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import datetime
import time
import signal

from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools

from datacore import *
from common import *
from common2 import *

import mistctrl                       # milestone control module for new project
import mistnavi

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALLBACK CONTROL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The en/disable selection callbacks apply to the selection change in the
# project list table. This is used in the reloadTable method when crearing the
# table. We don't want stray callbacks messing up things, do we?

@logger('enableSelectionCallback()')
def enableSelectionCallback():

    m = dc.x.project.selection_model.v
    m.selectionChanged.connect(onSelectionChanged)

@logger('disableSelectionCallback()')
def disableSelectionCallback():

    m = dc.x.project.selection_model.v

# The edit control callbacks are switched off when a new project is selected in
# the project table. This is reqired to avoid infinite loops and gremlins eating
# the application.

@logger('enableEditCallbacks()')
def enableEditCallbacks():

    # edit callbacks
    w, m = dc.ui.project.v, dc.m.project.v
    w.line_project_name.textChanged                 .connect(m.onProjectNameChanged)
    w.cb_project_type.currentIndexChanged[str]      .connect(m.onProjectTypeChanged)
    w.cb_project_category.currentIndexChanged[str]  .connect(m.onProjectCategoryChanged)
    w.sb_project_priority.valueChanged[int]         .connect(m.onProjectPriorityChanged)
    w.sb_project_challenge.valueChanged[int]        .connect(m.onProjectChallengeChanged)
    w.text_project_info.textChanged                 .connect(m.onProjectDescriptionChanged)

@logger('disableEditCallbacks()')
def disableEditCallbacks():

    # edit callbacks
    w, m = dc.ui.project.v, dc.m.project.v
    w.line_project_name.textChanged                 .disconnect(m.onProjectNameChanged)
    w.cb_project_type.currentIndexChanged[str]      .disconnect(m.onProjectTypeChanged)
    w.cb_project_category.currentIndexChanged[str]  .disconnect(m.onProjectCategoryChanged)
    w.sb_project_priority.valueChanged[int]         .disconnect(m.onProjectPriorityChanged)
    w.sb_project_challenge.valueChanged[int]        .disconnect(m.onProjectChallengeChanged)
    w.text_project_info.textChanged                 .disconnect(m.onProjectDescriptionChanged)

# This one enables all callbacks (including the above ones) and is used at
# startup.

@logger('enableAllCallbacks()')
def enableAllCallbacks():

    # menu callbacks
    w, m = dc.ui.project.v, dc.m.project.v
    w.btn_project_new           .clicked.connect(m.onNewProjectClicked)
    w.btn_project_delete        .clicked.connect(m.onDeleteSelectedProject)

    w.btn_doc_new       .clicked.connect(dc.m.document.v.onNewDocumentClicked)
    w.btn_doc_save_as   .clicked.connect(dc.m.document.v.onSaveAsClicked)
    w.btn_doc_open      .clicked.connect(dc.m.document.v.onOpenClicked)
    w.btn_doc_open_last .clicked.connect(dc.m.document.v.onOpenLastClicked)
    w.btn_doc_save      .clicked.connect(dc.m.document.v.onSaveClicked)

    # filter callbacks
    w = dc.ui.project.v
    w.btn_prio_low          .toggled.connect(onPriorityLowToggled)
    w.btn_prio_medium       .toggled.connect(onPriorityMediumToggled)
    w.btn_prio_high         .toggled.connect(onPriorityHighToggled)
    w.btn_challenge_low     .toggled.connect(onChallengeLowToggled)
    w.btn_challenge_medium  .toggled.connect(onChallengeMediumToggled)
    w.btn_challenge_hard    .toggled.connect(onChallengeHighToggled)

    # general gui callbacks
    w = dc.ui.project.v
    w.btn_info_max              .toggled.connect(onInfoMaxToggled)
    w.btn_project_sort_modified .clicked.connect(onSortProjectList)

    # edit / selection
    enableEditCallbacks()
    enableSelectionCallback()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY CALLBACK IMPLEMENTATIONS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class util: pass

# Even more callbacks! This time, it's the onFoo..() callback slot
# implementations.

# We begin with the project list table filter  These update the
# filter sets in the datacore and call reloadTable to update the view.

@logger('onPriorityLowToggled(checked)', 'checked')
def onPriorityLowToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.priority.v |= {1, 2, 3}
    else:
        dc.c.project.filters.priority.v -= {1, 2, 3}

    projectlist.reloadTable()

@logger('onPriorityMediumToggled(checked)', 'checked')
def onPriorityMediumToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.priority.v |= {4, 5, 6}
    else:
        dc.c.project.filters.priority.v -= {4, 5, 6}

    projectlist.reloadTable()

@logger('onPriorityHighToggled(checked)', 'checked')
def onPriorityHighToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.priority.v |= {7, 8, 9}
    else:
        dc.c.project.filters.priority.v -= {7, 8, 9}

    projectlist.reloadTable()

@logger('onChallengeLowToggled(checked)', 'checked')
def onChallengeLowToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.challenge.v |= {1, 2, 3}
    else:
        dc.c.project.filters.challenge.v -= {1, 2, 3}

    projectlist.reloadTable()

@logger('onChallengeMediumToggled(checked)', 'checked')
def onChallengeMediumToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.challenge.v |= {4, 5, 6}
    else:
        dc.c.project.filters.challenge.v -= {4, 5, 6}

    projectlist.reloadTable()

@logger('onChallengeHighToggled(checked)', 'checked')
def onChallengeHighToggled(checked):

    if dc.auto.v:
        return

    if checked:
        dc.c.project.filters.challenge.v |= {7, 8, 9}
    else:
        dc.c.project.filters.challenge.v -= {7, 8, 9}

    projectlist.reloadTable()

# Maximize / restore callback for infox maximization toggle.

@logger('NxProject.onInfoMaxToggled(state)', 'state')
def onInfoMaxToggled(state):
    if state:
        dc.states.project.maximized.v = True
        dc.m.project.v.updateStates('onInfoMaxToggled')
    else:
        dc.states.project.maximized.v = False
        dc.m.project.v.updateStates('onInfoMaxToggled')

# Sort by modification date when control is clicked.

@logger('NxProject.onSortProjectList()')
def onSortProjectList():
        dc.x.project.horizontal_header.v.setSortIndicator(
                projectlist.colModified,
                PySide.QtCore.Qt.SortOrder.DescendingOrder)

# Selected project changed -> update selected project edit controls and
# selected project label. Update selected project runtime data.

@logger('NxProject.onSelectionChanged(new, old)', 'new', 'old')
def onSelectionChanged(new, old):

    if dc.auto.v:
        return

    # check for valid index
    indexes = new.indexes()
    if not indexes or not dc.spid.v:
        dc.states.project.selected.v = False
        dc.m.project.v.updateStates('onSelectionChanged')
        return

    # get selected pid from table model
    index = indexes[0]
    pid = int(dc.x.project.model.v.itemFromIndex(index).text())
    if pid != dc.spid.v or dc.states.project.newload.v:

        dc.states.project.newload.v = False

        dc.spid.v = pid
        dc.sp = dc.s._(dc.spid.v)
        dc.s.spid.v = dc.spid.v

        # populate edit fields on selection change
        disableEditCallbacks()
        dc.auto.v = True
        dc.ui.project.v.line_project_name.setText(dc.sp.name.v)
        dc.ui.project.v.line_selected_project.setText(dc.sp.name.v)
        dc.ui.project.v.sb_project_priority.setValue(dc.sp.priority.v)
        dc.ui.project.v.sb_project_challenge.setValue(dc.sp.challenge.v)
        dc.ui.project.v.cb_project_type.setCurrentIndex(
                dc.ui.project.v.cb_project_type.findText(dc.sp.ptype.v))
        dc.ui.project.v.cb_project_category.setCurrentIndex(
                dc.ui.project.v.cb_project_category.findText(dc.sp.category.v))
        dc.ui.project.v.text_project_info.setText(dc.sp.description.v)
        dc.auto.v = False
        enableEditCallbacks()

    row = index.row()
    if row != dc.x.project.row.v:

        dc.states.project.selected.v = True
        dc.m.project.v.updateStates('onSelectionChanged')
        dc.x.project.row.v = row

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class projectlist: pass

# header labels for the project list table
projectlist.headers =  [
    'ID',
    'Name',
    'Type',
    'Version',
    'Category',
    'Priority',
    'Challenge',
    'Modified',
    'Created'
]

# This method set's up the project list table. It creates the model and sets
# up all necessary attributes. It is called from the NxProject __init__
# method. One only.

@logger('projectlist.initTable()')
def initTable():

    dc.x.project.view.v = dc.ui.project.v.tbl_project_list
    dc.x.project.model.v = QStandardItemModel()
    dc.x.project.view.v.setModel(dc.x.project.model.v)
    dc.x.project.model.v.setHorizontalHeaderLabels(projectlist.headers)
    dc.x.project.selection_model.v   = dc.x.project.view.v.selectionModel()
    dc.x.project.horizontal_header.v = dc.x.project.view.v.horizontalHeader()

@logger('projectlist.initProjectFilterControls()')
def initProjectFilterControls():

    # restore table sorting and headers widths
    loadLayout('project')

    # restore filter control states
    if 1 in dc.c.project.filters.priority.v:
        dc.ui.project.v.btn_prio_low.setChecked(True)
    if 4 in dc.c.project.filters.priority.v:
        dc.ui.project.v.btn_prio_medium.setChecked(True)
    if 7 in dc.c.project.filters.priority.v:
        dc.ui.project.v.btn_prio_high.setChecked(True)
    if 1 in dc.c.project.filters.challenge.v:
        dc.ui.project.v.btn_challenge_low.setChecked(True)
    if 4 in dc.c.project.filters.challenge.v:
        dc.ui.project.v.btn_challenge_medium.setChecked(True)
    if 7 in dc.c.project.filters.challenge.v:
        dc.ui.project.v.btn_challenge_hard.setChecked(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# used in with setTableValue
projectlist.colPid       = 0
projectlist.colName      = 1
projectlist.colType      = 2
projectlist.colVersion   = 3
projectlist.colCategory  = 4
projectlist.colPritoriy  = 5
projectlist.colChallenge = 6
projectlist.colModified  = 7
projectlist.colCreated   = 8

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@logger('projectlist.reloadTable(toggled=False)')
def reloadTable(toggled=False):

    dc.ui.project.v.tbl_project_list.setFocus()

    saveLayout('project')

    autoprev = dc.auto.v
    dc.auto.v = True

    # clear table
    disableSelectionCallback()
    dc.x.project.model.v.clear()
    dc.x.project.selection_model.v.reset()
    enableSelectionCallback()
    dc.x.project.model.v.setHorizontalHeaderLabels(projectlist.headers)

    dc.auto.v = autoprev

    # populate table with projects (that are in filter selection)
    # we start off by iterating through all projects

    for pid in dc.s.index.pid.v:

        # skip to next for filtered out entries
        if dc.s._(pid).priority.v not in dc.c.project.filters.priority.v:
            dc.spid.v = 0
            dc.sp = None
            continue
        if dc.s._(pid).challenge.v not in dc.c.project.filters.challenge.v:
            dc.spid.v = 0
            dc.sp = None
            continue

        # add pid to table
        major, minor = dc.s._(pid).m.active.v
        version = mistnavi.computeMinorLabelItems(pid, major, minor).shortlabel
        dc.x.project.model.v.insertRow(0, [
            QStandardItem(str(pid).zfill(4)),
            QStandardItem(dc.s._(pid).name.v),
            QStandardItem(dc.s._(pid).ptype.v),
            QStandardItem(version),
            QStandardItem(dc.s._(pid).category.v),
            QStandardItem(str(dc.s._(pid).priority.v)),
            QStandardItem(str(dc.s._(pid).challenge.v)),
            QStandardItem(convert(dc.s._(pid).modified.v)),
            QStandardItem(convert(dc.s._(pid).created.v)) ])

    # now we have the table as required, now set the selection This is a bit
    # tricky at times. If we have the selection within the visible with the
    # current filter settings, then we just search and select that line.
    # Otherwise we select the first line and have to set the selection data
    # too (dc.spid.v / dc.sp).

    # we don't select anything if we don't have rows
    rowcount = dc.x.project.model.v.rowCount()
    dc.states.project.noupdate.v = True
    if rowcount <= 0:

        dc.x.project.row.v = -1
        dc.states.project.selected.v = False

    # we don't have a selected project id (outside the filter or deleted)
    elif not dc.spid.v:

        index = dc.x.project.model.v.index(0, 0)
        pid = int(dc.x.project.model.v.data(index))
        dc.spid.v = pid
        dc.sp = dc.s._(pid)

        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.project.selection_model.v.setCurrentIndex(index, s|r)
        # note: this triggers onSelectionChanged
        selection = dc.x.project.view.v.selectionModel().selection()

    else:

        for rowcnt in range(dc.x.project.model.v.rowCount()):

            index = dc.x.project.model.v.index(rowcnt, 0)
            pid = int(dc.x.project.model.v.data(index))

            # if we have a match, select it and abort
            if pid == dc.spid.v:

                s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                dc.x.project.selection_model.v.setCurrentIndex(index, s|r)
                # note: this triggers onSelectionChanged
                selection = dc.x.project.view.v.selectionModel().selection()
                break

    loadLayout('project')
    dc.states.project.noupdate.v = False
    dc.m.project.v.updateStates('reloadTable')

projectlist.initTable = initTable
projectlist.initProjectFilterControls = initProjectFilterControls
projectlist.reloadTable = reloadTable
dc.m.project.projectlist.v = projectlist

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EVENT FILTERS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class EfNameFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.name.v and dc.sp != None:
                dc.m.log.v.addAutoLog('Track', 'Name changed',
                        'Project name changed to {}'.format(dc.sp.name.v))
            dc.x.project.changeflag.name.v = False
        return QObject.eventFilter(self, obj, event)
ef_name_focus_out = EfNameFocusOut()

class EfCategoryFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.category.v and dc.sp != None:
                dc.m.log.v.addAutoLog('Track', 'Category changed',
                        'Project category changed to {}'.format(dc.sp.category.v))
            dc.x.project.changeflag.category.v = False
        return QObject.eventFilter(self, obj, event)
ef_category_focus_out = EfCategoryFocusOut()

class EfTypeFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.ptype.v and dc.sp != None:
                dc.m.log.v.addAutoLog('Track', 'Type changed',
                        'Project type changed to {}'.format(dc.sp.ptype.v))
            dc.x.project.changeflag.ptype.v = False
        return QObject.eventFilter(self, obj, event)
ef_type_focus_out = EfTypeFocusOut()

class EfPriorityFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.priority.v and dc.sp != None:
                dc.m.log.v.addAutoLog('Track', 'Priority changed',
                        'Project priority changed to {}'.format(dc.sp.priority.v))
            dc.x.project.changeflag.priority.v = False
        return QObject.eventFilter(self, obj, event)
ef_priority_focus_out = EfPriorityFocusOut()

class EfChallengeFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.challenge.v and dc.sp != None:
                dc.m.log.v.addAutoLog('Track', 'Challenge changed',
                        'Project challenge changed to {}'.format(dc.sp.challenge.v))
            dc.x.project.changeflag.challenge.v = False
        return QObject.eventFilter(self, obj, event)
ef_challenge_focus_out = EfChallengeFocusOut()

class EfProjectDescriptionFocusOut(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            if dc.x.project.changeflag.project_description.v and dc.sp != None:
                description = dc.ui.project.v.text_project_info.toHtml()
                dc.sp.description.v = description
            dc.x.project.changeflag.project_description.v = False
        return QObject.eventFilter(self, obj, event)
ef_project_deisription_focus_out = EfProjectDescriptionFocusOut()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxProject():

    # Init class. Not much to see here. Just set some starting values, apply
    # state and enable

    @logger('NxProject.__init__(self)', 'self')
    def __init__(self):

        dc.m.project.v = self

        # These are used in the project states callbacks for the filter buttons
        # and the reloadTable method in the table list.
        if not isinstance(dc.c.project.filters.priority.v, set):
            dc.c.project.filters.priority.v = {1, 2, 3, 4, 5, 6, 7, 8, 9}
            dc.c.project.filters.challenge.v = {1, 2, 3, 4, 5, 6, 7, 8, 9}

        # apply state (enable/dissable widgets)
        dc.spid.v = 0
        projectlist.initTable()

        if dc.c.config.loaded.v:
            loadLayout('project')

        dc.states.project.changed.v     = False
        dc.states.project.focustable.v  = False
        dc.states.project.maximized.v   = False
        dc.states.project.newproject.v  = False
        dc.states.project.noupdate.v    = False
        dc.states.project.selected.v    = False
        dc.states.project.newload.v     = False
        dc.states.project.startup.v     = True
        self.updateStates('__init__')

        enableAllCallbacks()

        dc.x.project.changeflag.name.v = False
        dc.x.project.changeflag.ptype.v = False
        dc.x.project.changeflag.category.v = False
        dc.x.project.changeflag.priority.v = False
        dc.x.project.changeflag.challenge.v = False
        dc.x.project.changeflag.project_description.v = False
        dc.ui.project.v.line_project_name.installEventFilter(ef_name_focus_out)
        dc.ui.project.v.cb_project_type.installEventFilter(ef_type_focus_out)
        dc.ui.project.v.cb_project_category.installEventFilter(ef_category_focus_out)
        dc.ui.project.v.sb_project_priority.installEventFilter(ef_priority_focus_out)
        dc.ui.project.v.sb_project_challenge.installEventFilter(ef_challenge_focus_out)
        dc.ui.project.v.text_project_info.installEventFilter(ef_project_deisription_focus_out)

    @logger('NxProject.initNavi(self)', 'self')
    def initNavi(self):

        dc.ui.project.v.btn_show_logs.clicked.connect(dc.m.log.v.onShow)
        dc.ui.project.v.btn_show_roadmap.clicked.connect(dc.m.roadmap.v.onShow)

    @logger('NxProject.onShow(self)', 'self')
    def onShow(self):

        dc.ui.log.v.setParent(None)
        dc.ui.roadmap.v.setParent(None)
        dc.ui.main.v.setCentralWidget(dc.ui.project.v)
        projectlist.reloadTable()

    @logger('NxProject.updateStates(self, source)', 'self', 'source')
    def updateStates(self, source):

        if dc.states.project.noupdate.v == True:

            return

        if dc.states.project.startup.v:

            applyStates({
                'btn_info_max'          : {'enabled': False},
                'btn_doc_new'           : {'enabled': True},
                'btn_doc_open'          : {'enabled': True},
                'btn_doc_save'          : {'enabled': False},
                'btn_doc_open_last'     : {'enabled': False},
                'btn_doc_save_as'       : {'enabled': True},
                'btn_project_delete'    : {'enabled': False},
                'btn_project_new'       : {'enabled': True},
                'btn_show_roadmap'      : {'enabled': False},
                'btn_show_logs'         : {'enabled': False},
                'tbl_project_list'      : {'enabled': True},
                'selected_project_group': {'enabled': False},
                'line_selected_project' : {'clear': True},
                'line_project_name'     : {'clear': True},
                'text_project_info'     : {'clear': True},
                'cb_project_type'       : {'index': 0},
                'cb_project_category'   : {'index': 0},
                'sb_project_priority'   : {'value': 1},
                'sb_project_challenge'  : {'value': 1}}, dc.ui.project.v)

            if os.path.exists(str(dc.c.lastpath.v)):

                applyStates({'btn_doc_open_last': {'enabled': True}},
                            dc.ui.project.v)

            dc.states.project.startup.v = False
            return

        if dc.states.project.newproject.v:

            applyStates({
                'btn_info_max'          : {'enabled': True},
                'line_selected_project' : {'clear': True},
                'line_project_name'     : {'clear': True},
                'text_project_info'     : {'clear': True},
                'cb_project_type'       : {'index': 0},
                'cb_project_category'   : {'index': 0},
                'sb_project_priority'   : {'value': 1},
                'sb_project_challenge'  : {'value': 1}}, dc.ui.project.v)

            dc.states.project.newproject.v = False

        if dc.states.project.maximized.v:
            applyStates({
                'btn_info_max'          : {'enabled': True},
                'btn_doc_new'           : {'enabled': False},
                'btn_doc_open'          : {'enabled': False},
                'btn_doc_open_last'     : {'enabled': False},
                'btn_doc_save'          : {'enabled': False},
                'btn_doc_save_as'       : {'enabled': False},
                'btn_project_delete'    : {'enabled': False},
                'btn_project_new'       : {'enabled': False},
                'btn_show_roadmap'      : {'enabled': False},
                'btn_show_logs'         : {'enabled': False},
                'project_meta': {'visible': False, 'enabled': True},
                'project_list': {'visible': False, 'enabled': True},
                'gl_info':      {'margins': (0, 0, 15, 0)}}, dc.ui.project.v)
            return

        if dc.states.project.selected.v:
            applyStates({
                'btn_info_max'          : {'enabled': True},
                'btn_doc_new'           : {'enabled': True},
                'btn_doc_open'          : {'enabled': True},
                'btn_doc_open_last'     : {'enabled': False},
                'btn_doc_save'          : {'enabled': False},
                'btn_doc_save_as'       : {'enabled': True},
                'btn_project_delete'    : {'enabled': True},
                'btn_project_new'       : {'enabled': True},
                'btn_show_roadmap'      : {'enabled': True},
                'tbl_project_list'      : {'enabled': True},
                'selected_project_group': {'enabled': True},
                'project_meta'          : {'visible': True, 'enabled': True},
                'project_list'          : {'visible': True, 'enabled': True},
                'gl_info'               : {'margins': (0, 0, 0, 0)},
                'btn_show_logs'         : {'enabled': True}}, dc.ui.project.v)
        else:
            applyStates({
                'btn_info_max'          : {'enabled': False},
                'btn_doc_new'           : {'enabled': True},
                'btn_doc_open'          : {'enabled': True},
                'btn_doc_open_last'     : {'enabled': False},
                'btn_doc_save'          : {'enabled': False},
                'btn_doc_save_as'       : {'enabled': True},
                'btn_project_delete'    : {'enabled': False},
                'btn_project_new'       : {'enabled': True, 'focused': True},
                'btn_show_roadmap'      : {'enabled': False},
                'btn_show_logs'         : {'enabled': False},
                'tbl_project_list'      : {'enabled': True},
                'selected_project_group': {'enabled': False},
                'project_meta'          : {'visible': True, 'enabled': True},
                'project_list'          : {'visible': True, 'enabled': True},
                'gl_info'               : {'margins': (0, 0, 0, 0)},
                'line_selected_project' : {'clear': True},
                'line_project_name'     : {'clear': True},
                'cb_project_type'       : {'index': 0},
                'cb_project_category'   : {'index': 0},
                'sb_project_priority'   : {'value': 1},
                'sb_project_challenge'  : {'value': 1}}, dc.ui.project.v)

        if dc.states.project.changed.v:
            applyStates({'btn_doc_save': {'enabled': True}}, dc.ui.project.v)
        else:
            applyStates({'btn_doc_save': {'enabled': False}}, dc.ui.project.v)

        if dc.states.project.focustable.v:

            dc.states.project.focustable.v = False
            applyStates({
                'tbl_project_list': {'enabled': True, 'focused': True}},
                dc.ui.project.v)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Updates the project modification date in the project table and sets the
    # changed value. This is called by all persistent data operations of the
    # document.

    @logger('NxProject.touchProject(self, source=\'Unknown\')', 'self')
    def touchProject(self, source):

        timestamp = int(time.time())
        dc.sp.modified.v = timestamp
        dc.states.project.changed.v = True
        setTableValue('project', projectlist.colModified, convert(timestamp))
        self.updateStates('touchProject')

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The following callbacks are used when currently selected project
    # attributes are changed in the left hand pane.

    @logger('NxProject.onProjectNameChanged(self, name)', 'self', 'name')
    def onProjectNameChanged(self, name):

        if dc.auto.v:
            return

        dc.sp.name.v = name
        dc.ui.project.v.line_selected_project.setText(name)
        self.touchProject('onProjectNameChanged')
        setTableValue('project', projectlist.colName, name)
        dc.x.project.changeflag.name.v = True # used for unFocus callback (log)

    @logger('NxProject.onProjectTypeChanged(self, ptype)', 'self', 'ptype')
    def onProjectTypeChanged(self, ptype):

        if dc.auto.v:
            return

        dc.sp.ptype.v = ptype
        self.touchProject('onProjectTypeChanged')
        setTableValue('project', projectlist.colType, ptype)
        dc.x.project.changeflag.ptype.v = True # used for unFocus callback (log)

    @logger('NxProject.onProjectCategoryChanged(self, category)',
            'self', 'category')
    def onProjectCategoryChanged(self, category):

        if dc.auto.v:
            return

        dc.sp.category.v = category
        self.touchProject('onProjectCategoryChanged')
        setTableValue('project', projectlist.colCategory, category)
        dc.x.project.changeflag.category.v = True # used for unFocus callback (log)

    @logger('NxProject.onProjectPriorityChanged(self, priority)',
            'self', 'priority')
    def onProjectPriorityChanged(self, priority):

        if dc.auto.v:
            return

        dc.sp.priority.v = priority
        self.touchProject('onProjectPriorityChanged')
        setTableValue('project', projectlist.colPritoriy, str(priority))
        dc.x.project.changeflag.priority.v = True # used for unFocus callback (log)

    @logger('NxProject.onProjectChallengeChanged(self, challenge)',
            'self', 'challenge')
    def onProjectChallengeChanged(self, challenge):

        if dc.auto.v:
            return

        dc.sp.challenge.v = challenge
        self.touchProject('onProjectChallengeChanged')
        setTableValue('project', projectlist.colChallenge, str(challenge))
        dc.x.project.changeflag.challenge.v = True # used for unFocus callback (log)

    @logger('NxProject.onProjectDescriptionChanged(self)', 'self')
    def onProjectDescriptionChanged(self):

        if dc.auto.v:
            return

        self.touchProject('onProjectDescriptionChanged')
        dc.x.project.changeflag.project_description.v = True

    # Create a new project

    @logger('NxProject.onNewProjectClicked(self)', 'self')
    def onNewProjectClicked(self):

        # prepare
        timestamp = int(time.time())
        pid = dc.s.nextpid.v

        # init project control data
        dc.s.index.pid.v.add(pid)
        dc.s.nextpid.v += 1
        dc.spid.v = pid
        dc.sp = dc.s._(pid)
        dc.s.spid.v = dc.spid.v

        # init milestone control data
        mistctrl.mistctrl_new_tree()

        # set priority
        dc.sp.priority.v  = 1
        dc.sp.challenge.v = 1
        dc.sp.name.v = ''
        dc.sp.ptype.v = 'Application'
        dc.sp.category.v = 'Development'

        # init project attributes
        dc.sp.created.v     = timestamp
        dc.sp.modified.v    = timestamp

        # init log control data
        dc.sp.nextlid.v     = 1
        dc.sp.log.index.v   = set()

        # set state
        dc.states.project.changed.v = True
        dc.states.project.newproject.v = True
        dc.x.project.changeflag.name.v = False
        projectlist.reloadTable()

        dc.m.log.v.addAutoLog('Track', 'Project created',
                              'Project has been created')

        # states refuses to set this the first time, second is fine though..
        # weird. Setting manually.
        dc.ui.project.v.line_project_name.setFocus()

    # Delete selected project

    @logger('NxProject.onDeleteSelectedProject(self)', 'self')
    def onDeleteSelectedProject(self):

        # are you sure? dialog
        t = 'Delete project?'
        q = 'Sure you want to delete project {}: {}?'\
                .format(str(dc.spid.v), dc.sp.name.v)
        yes, no = QMessageBox.Yes, QMessageBox.No
        response = QMessageBox.question(dc.ui.project.v, t, q, yes|no)
        if response == QMessageBox.StandardButton.No:
            return

        # remove project from index
        dc.s.index.pid.v.remove(dc.spid.v)
        del dc.s.__dict__['_{}'.format(dc.spid.v)]
        dc.spid.v = 0

        # state
        dc.states.project.changed.v = True
        dc.states.project.focustable.v = True
        projectlist.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxDocument:

    @logger('NxDocument.__init__(self)', 'self')
    def __init__(self):

        dc.m.document.v = self
        self.reset()

        dc.x.app.v.aboutToQuit.connect(dc.m.document.v.onAboutToQuit)
        signal.signal(signal.SIGTERM, self.onSigTerm)

    @logger('NxDocument.onSigTerm(self, num, frame)', 'self', 'num', 'frame')
    def onSigTerm(self, num, frame):

        QApplication.quit()

    @logger('NxDocument.onAboutToQuit(self)', 'self')
    def onAboutToQuit(self):

        if dc.states.project.changed.v:
            if dc.x.path.v:
                dcsave()
            else:
                t = 'Save Document?'
                q = 'Do you want to save the document before exiting?'
                yes, no = QMessageBox.Yes, QMessageBox.No
                response = QMessageBox.question(dc.ui.project.v, t, q, yes|no)
                if response == QMessageBox.StandardButton.Yes:
                    t = 'Save nelia1 document'
                    q = 'Nelia Files (*{})'.format(dc.x.extension.v)
                    path = QFileDialog.getSaveFileName(dc.ui.main.v, t, dc.x.default.path.v, q)[0]
                    if path == '':
                        return
                    extension_start = len(path) - len(dc.x.extension.v)
                    if path.rfind(dc.x.extension.v) != extension_start:
                        path += dc.x.extension.v
                    result = dcsave(path)
                    dc.x.path.v = path
        dcsaveconfig()

    @logger('NxDocument.reset(self)', 'self')
    def reset(self):

        del dc.__dict__['s']

        # some initial values for datacore (application specific)
        dc.x.path.v = None
        dc.x.extension.v = '.nelia1'
        dc.x.default.path.v = os.path.expanduser('~/Documents')
        dc.s.nextpid.v = 1
        dc.s.index.pid.v = set()

        dc.spid.v = 0

        dc.x.log.slid.v = 0
        dc.x.roadmap.smiid.v = 0

    @logger('NxDocument.onNewDocumentClicked(self)', 'self')
    def onNewDocumentClicked(self):

        if dc.states.project.changed.v:
            q = 'Discard changes?'
            m = 'Creating a new document will discard your changes. ' \
                + 'Do you want to proceed?'
            yes, no = QMessageBox.Yes, QMessageBox.No
            response = QMessageBox.question(dc.ui.main.v, q, m, yes|no)
            if response == QMessageBox.StandardButton.No:
                return
        self.reset()
        dc.states.project.newproject.v = True
        dc.states.project.focustable.v = True
        dc.m.project.projectlist.v.reloadTable()

    @logger('NxDocument.onSaveAsClicked(self)', 'self')
    def onSaveAsClicked(self):

        t = 'Save nelia1 document'
        q = 'Nelia Files (*{})'.format(dc.x.extension.v)
        path = QFileDialog.getSaveFileName(dc.ui.main.v, t, dc.x.default.path.v, q)[0]
        if path == '':
            return
        extension_start = len(path) - len(dc.x.extension.v)
        if path.rfind(dc.x.extension.v) != extension_start:
            path += dc.x.extension.v
        result = dcsave(path)
        if isinstance(result, Exception):
            title, message = 'Save failed', 'Save failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        dc.x.path.v = path
        dc.states.project.changed.v = False
        dc.states.project.focustable.v = True
        dc.m.project.v.updateStates('onSaveAsClicked')

    @logger('NxDocument.onSaveClicked(self)', 'self')
    def onSaveClicked(self):

        if dc.x.path.v:
            result = dcsave(dc.x.path.v)
            if isinstance(result, Exception):
                title, message = 'Save failed', 'Save failed! ' + str(result)
                QMessageBox.critical(dc.ui.main.v, title, message)
                return
            dc.states.project.changed.v = False
            dc.states.project.focustable.v = True
            dc.m.project.v.updateStates('onSaveClicked')
        else:
            self.onSaveAsClicked()

    @logger('NxDocument.onOpenClicked(self)', 'self')
    def onOpenClicked(self):

        if dc.states.project.changed.v:
            q = 'Discard changes?'
            m = 'Opening a file will discard your changes. ' \
                + 'Do you want to proceed?'
            yes, no = QMessageBox.Yes, QMessageBox.No
            response = QMessageBox.question(dc.ui.main.v, q, m, yes|no)
            if response == QMessageBox.StandardButton.No:
                return

        title  = 'Open nelia1 document'
        select = 'Nelia Files (*{})'.format(dc.x.extension.v)
        path = QFileDialog.getOpenFileName(
            dc.ui.project.v, title, dc.x.default.path.v, select)[0]
        if not path:
            return

        result = dcload(path)
        if isinstance(result, Exception):
            title, message = 'open failed', 'open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            dc.x.path.v = None
            return

        dc.c.lastpath.v = path
        dc.spid.v = dc.s.spid.v
        dc.sp = dc.s._(dc.spid.v)
        dc.states.project.newproject.v = True
        dc.states.project.changed.v = False
        dc.states.project.focustable.v = True
        dc.states.project.newload.v = True
        dc.m.project.v.updateStates('NxDocument.onOpenClicked')
        dc.m.project.projectlist.v.reloadTable()

    @logger('NxDocument.onOpenLastClicked(self)', 'self')
    def onOpenLastClicked(self):

        result = dcload(dc.c.lastpath.v)
        if isinstance(result, Exception):
            title, message = 'Open failed', 'Open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        dc.spid.v = dc.s.spid.v
        dc.sp = dc.s._(dc.spid.v)
        dc.states.project.changed.v = False
        dc.states.project.focustable.v = True
        dc.states.project.newload.v = True
        dc.m.project.projectlist.v.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

