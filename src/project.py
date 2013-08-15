# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file contains the business end of the project widget. This manages the
# documents and the projects within the documents.
#
# states
# callbacks
# projectlist
# NxProject
# NxDocument
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# STATES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# We start with the declaration of the widget states.
# These are applield with the applyStates method from the common module.
# applyStates(states.startup, dc.ui.project.v)

class states: pass

# Did I mention that the names I come up with are a bit vague sometimes? So this
# is the startup state. The state is set on startup.. and on load documnt.. and
# on last project delete.

states.startup = {
        'btn_doc_new'           : {'visible': True, 'enabled': False},
        'btn_doc_open'          : {'visible': True, 'enabled': True},
        'btn_doc_open_last'     : {'visible': True, 'enabled': False},
        'btn_doc_save_as'       : {'visible': True, 'enabled': False},
        'btn_project_delete'    : {'visible': True, 'enabled': False},
        'btn_project_new'       : {'visible': True, 'enabled': True},
        'btn_show_roadmap'      : {'visible': True, 'enabled': False},
        'btn_show_logs'         : {'visible': True, 'enabled': False},
        'tbl_project_list'      : {'visible': True, 'enabled': True},
        'selected_project_group': {'visible': True, 'enabled': False},
        'line_selected_project' : {'clear': True},
        'line_project_name'     : {'clear': True},
        'cb_project_type'       : {'index': 0},
        'cb_project_category'   : {'index': 0},
        'sb_project_priority'   : {'value': 1},
        'sb_project_challenge'  : {'value': 1}
    }

# If the loaded configuration contains the path to a last saved document, enable
# this control. Sub-state to startup. Is disaled once a project is selected.
# This is a substate of startup.

states.last = {
    'btn_doc_open_last'     : {'visible': True, 'enabled': True},
}

# Once a project is created or a document is loaded (wich implies a selected
# project), the project controls are enabled and the document can be saved.

states.selected = {
    'btn_doc_new'           : {'visible': True, 'enabled': True},
    'btn_doc_open'          : {'visible': True, 'enabled': True},
    'btn_doc_open_last'     : {'visible': True, 'enabled': False},
    'btn_doc_save_as'       : {'visible': True, 'enabled': True},
    'btn_project_delete'    : {'visible': True, 'enabled': True},
    'btn_project_new'       : {'visible': True, 'enabled': True},
    'btn_show_roadmap'      : {'visible': True, 'enabled': True},
    'btn_show_logs'         : {'visible': True, 'enabled': True},
    'tbl_project_list'      : {'visible': True, 'enabled': True},
    'selected_project_group': {'visible': True, 'enabled': True}
}

# Clean edit widgets when creating new project (make sure to create the project
# data structure before applying this) or you'll enjoy a trip to errorland.

states.new_project = {
    'line_selected_project' : {'text': 'Unnamed'},
    'line_project_name'     : {'text': 'Unnamed'},
    'cb_project_type'       : {'index': 0},
    'cb_project_category'   : {'index': 0},
    'sb_project_priority'   : {'value': 1},
    'sb_project_challenge'  : {'value': 1},
    'text_project_info'     : {'clear': True}
}

# There is a maximize toggle button on top of the selected project description
# text box. The following two states switch between normal and maximized for
# this widget (by hiding the project list and the edit widgets)

states.description_normal = {
    'project_meta': {'visible': True, 'enabled': True},
    'project_list': {'visible': True, 'enabled': True},
    'gl_info':      {'margins': (0, 0, 0, 0)}
}
states.description_maximized = {
    'project_meta': {'visible': False, 'enabled': True},
    'project_list': {'visible': False, 'enabled': True},
    'gl_info':      {'margins': (0, 0, 15, 0)}
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CALLBACK CONTROL
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Callbacks! All of them. The en/disable selection callbacks apply to the
# selection change in the project list table. This is used in the reloadTable
# method when crearing the table. We don't want stray callbacks messing up
# things, do we?

@logger('enableSelectionCallback()')
def enableSelectionCallback():

    m = dc.x.project.selection_model.v
    m.selectionChanged.connect(onSelectionChanged)

@logger('disableSelectionCallback()')
def disableSelectionCallback():

    m = dc.x.project.selection_model.v
    m.selectionChanged.disconnect(onSelectionChanged)

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

    # navi callbacks
    w = dc.ui.project.v
    w.btn_show_logs             .clicked.connect(onShowLogs)
    w.btn_show_roadmap          .clicked.connect(onShowRoadmap)

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

# Even more callbacks! This time, it's the onFoo..() callback slot
# implementations.

# We begin with the project list table filter  These update the
# filter sets in the datacore and call reloadTable to update the view.

@logger('onPriorityLowToggled(checked)', 'checked')
def onPriorityLowToggled(checked):
    if checked:
        dc.c.project.filters.priority.v.add(1)
        dc.c.project.filters.priority.v.add(2)
        dc.c.project.filters.priority.v.add(3)
    else:
        dc.c.project.filters.priority.v.discard(1)
        dc.c.project.filters.priority.v.discard(2)
        dc.c.project.filters.priority.v.discard(3)
    projectlist.reloadTable()

@logger('onPriorityMediumToggled(checked)', 'checked')
def onPriorityMediumToggled(checked):
    if checked:
        dc.c.project.filters.priority.v.add(4)
        dc.c.project.filters.priority.v.add(5)
        dc.c.project.filters.priority.v.add(6)
    else:
        dc.c.project.filters.priority.v.discard(4)
        dc.c.project.filters.priority.v.discard(5)
        dc.c.project.filters.priority.v.discard(6)
    projectlist.reloadTable()

@logger('onPriorityHighToggled(checked)', 'checked')
def onPriorityHighToggled(checked):
    if checked:
        dc.c.project.filters.priority.v.add(7)
        dc.c.project.filters.priority.v.add(8)
        dc.c.project.filters.priority.v.add(9)
    else:
        dc.c.project.filters.priority.v.discard(7)
        dc.c.project.filters.priority.v.discard(8)
        dc.c.project.filters.priority.v.discard(9)
    projectlist.reloadTable()

@logger('onChallengeLowToggled(checked)', 'checked')
def onChallengeLowToggled(checked):
    if checked:
        dc.c.project.filters.challenge.v.add(1)
        dc.c.project.filters.challenge.v.add(2)
        dc.c.project.filters.challenge.v.add(3)
    else:
        dc.c.project.filters.challenge.v.discard(1)
        dc.c.project.filters.challenge.v.discard(2)
        dc.c.project.filters.challenge.v.discard(3)
    projectlist.reloadTable()

@logger('onChallengeMediumToggled(checked)', 'checked')
def onChallengeMediumToggled(checked):
    if checked:
        dc.c.project.filters.challenge.v.add(4)
        dc.c.project.filters.challenge.v.add(5)
        dc.c.project.filters.challenge.v.add(6)
    else:
        dc.c.project.filters.challenge.v.discard(4)
        dc.c.project.filters.challenge.v.discard(5)
        dc.c.project.filters.challenge.v.discard(6)
    projectlist.reloadTable()

@logger('onChallengeHighToggled(checked)', 'checked')
def onChallengeHighToggled(checked):
    if checked:
        dc.c.project.filters.challenge.v.add(7)
        dc.c.project.filters.challenge.v.add(8)
        dc.c.project.filters.challenge.v.add(9)
    else:
        dc.c.project.filters.challenge.v.discard(7)
        dc.c.project.filters.challenge.v.discard(8)
        dc.c.project.filters.challenge.v.discard(9)
    projectlist.reloadTable()

# Maximize / restore callback for infox maximization toggle.

@logger('NxProject.onInfoMaxToggled(state)', 'state')
def onInfoMaxToggled(state):
    if state:
        applyStates(states.description_maximized, dc.ui.project.v)
    else:
        applyStates(states.description_normal, dc.ui.project.v)

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

    # check for valid index
    indexes = new.indexes()
    if not indexes:
        return

    # get selected pid from table model
    index = indexes[0]
    dc.spid.v = int(dc.x.project.model.v.itemFromIndex(index).text())
    dc.sp = dc.s._(dc.spid.v)

    # populate edit fields on selection change
    disableEditCallbacks()
    dc.ui.project.v.line_project_name.setText(dc.sp.name.v)
    dc.ui.project.v.line_selected_project.setText(dc.sp.name.v)
    dc.ui.project.v.sb_project_priority.setValue(dc.sp.priority.v)
    dc.ui.project.v.sb_project_challenge.setValue(dc.sp.challenge.v)
    dc.ui.project.v.cb_project_type.setCurrentIndex(
            dc.ui.project.v.cb_project_type.findText(dc.sp.ptype.v))
    dc.ui.project.v.cb_project_category.setCurrentIndex(
            dc.ui.project.v.cb_project_category.findText(dc.sp.category.v))
    dc.ui.project.v.text_project_info.setText(dc.sp.description.v)
    enableEditCallbacks()

# switch to log and roadmap views
# I have decided to load the project logs / roadmap only when navigating to
# these widgets instead of real-time during selection change to avoid
# latency with larger entries. setParent(None) prevents a segfault.

@logger('onShowLogs()')
def onShowLogs():
    dc.ui.project.v.setParent(None)
    dc.m.log.onShown.v()
    dc.ui.main.v.setCentralWidget(dc.ui.log.v)

@logger('onShowRoadmap()')
def onShowRoadmap():
    dc.ui.project.v.setParent(None)
    dc.m.roadmap.states.v.onShown()
    dc.ui.main.v.setCentralWidget(dc.ui.roadmap.v)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UTILITY CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class projectlist:

    # header labels for the project list table
    headers =  [
        'ID',
        'Name',
        'Type',
        'Verson',
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

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # used in with setTableValue
    colPid       = 0
    colName      = 1
    colType      = 2
    colVersion   = 3
    colCategory  = 4
    colPritoriy  = 5
    colChallenge = 6
    colModified  = 7
    colCreated   = 8

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('projectlist.reloadTable(toggled=False)')
    def reloadTable(toggled=False):

        saveLayout('project')

        # clear table
        disableSelectionCallback()
        dc.x.project.model.v.clear()
        dc.x.project.selection_model.v.reset()
        enableSelectionCallback()
        dc.x.project.model.v.setHorizontalHeaderLabels(projectlist.headers)

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
            dc.x.project.model.v.insertRow(0, [
                QStandardItem(str(pid).zfill(4)),
                QStandardItem(dc.s._(pid).name.v),
                QStandardItem(dc.s._(pid).ptype.v),
                QStandardItem('{}.{}'.format(major, minor)),
                QStandardItem(dc.s._(pid).category.v),
                QStandardItem(str(dc.s._(pid).priority.v)),
                QStandardItem(str(dc.s._(pid).challenge.v)),
                QStandardItem(convert(dc.s._(pid).modified.v)),
                QStandardItem(convert(dc.s._(pid).created.v)) ])

        loadLayout('project')

        # now we have the table as required, now set the selection This is a bit
        # tricky at times. If we have the selection within the visible with the
        # current filter settings, then we just search and select that line.
        # Otherwise we select the first line and have to set the selection data
        # too (dc.spid.v / dc.sp).

        # we don't select anything if we don't have rows
        rowcount = dc.x.project.model.v.rowCount()
        if rowcount <= 0:
            disableEditCallbacks()
            applyStates(states.startup, dc.ui.project.v)
            return

        # we don't have a selected project id (outside the filter or deleted)
        if not dc.spid.v:
            index = dc.x.project.model.v.index(0, 0)
            pid = int(dc.x.project.model.v.data(index))
            dc.spid.v = pid
            dc.sp = dc.s._(pid)
            s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
            dc.x.project.selection_model.v.setCurrentIndex(index, s|r)
            selection = dc.x.project.view.v.selectionModel().selection()
            applyStates(states.selected, dc.ui.project.v)

        # iterate through table rows
        for rowcnt in range(dc.x.project.model.v.rowCount()):
            index = dc.x.project.model.v.index(rowcnt, 0)
            pid = int(dc.x.project.model.v.data(index))

            # if we have a match, select it and abort
            if pid == dc.spid.v:
                s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                dc.x.project.selection_model.v.setCurrentIndex(index, s|r)
                selection = dc.x.project.view.v.selectionModel().selection()
                break

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
        dc.c.project.filters.priority.v = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        dc.c.project.filters.challenge.v = {1, 2, 3, 4, 5, 6, 7, 8, 9}

        # apply state (enable/dissable widgets)
        dc.spid.v = 0
        projectlist.initTable()
        applyStates(states.startup, dc.ui.project.v)
        if dc.x.config.loaded.v:
            loadLayout('project')
            if dc.c.lastpath.v:
                applyStates(states.last, dc.ui.project.v)

        enableAllCallbacks()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Updates the project modification date in the project table and sets the
    # changed value. This is called by all persistent data operations of the
    # document.

    @logger('NxProject.touchProject(self)', 'self')
    def touchProject(self):

        timestamp = int(time.time())
        dc.sp.modified.v = timestamp
        dc.r.changed.v = True
        setTableValue('project',
                                  projectlist.colModified, convert(timestamp))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # The following callbacks are used when currently selected project
    # attributes are changed in the left hand pane.

    @logger('NxProject.onProjectNameChanged(self, name)', 'self', 'name')
    def onProjectNameChanged(self, name):

        dc.sp.name.v = name
        dc.ui.project.v.line_selected_project.setText(name)
        self.touchProject()
        setTableValue('project', projectlist.colName, name)

    @logger('NxProject.onProjectTypeChanged(self, ptype)', 'self', 'ptype')
    def onProjectTypeChanged(self, ptype):

        dc.sp.ptype.v = ptype
        self.touchProject()
        setTableValue('project', projectlist.colType, ptype)

    @logger('NxProject.onProjectCategoryChanged(self, category)',
            'self', 'category')
    def onProjectCategoryChanged(self, category):

        dc.sp.category.v = category
        self.touchProject()
        setTableValue('project', projectlist.colCategory, category)

    @logger('NxProject.onProjectPriorityChanged(self, priority)',
            'self', 'priority')
    def onProjectPriorityChanged(self, priority):

        dc.sp.priority.v = priority
        self.touchProject()
        setTableValue('project', projectlist.colPritoriy, str(priority))

    @logger('NxProject.onProjectChallengeChanged(self, challenge)',
            'self', 'challenge')
    def onProjectChallengeChanged(self, challenge):

        dc.sp.challenge.v = challenge
        self.touchProject()
        setTableValue('project', projectlist.colChallenge, str(challenge))

    @logger('NxProject.onProjectDescriptionChanged(self)', 'self')
    def onProjectDescriptionChanged(self):

        dc.sp.description.v = dc.ui.project.v.text_project_info.toHtml()
        self.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

        # init milestone control data
        mistctrl.mistctrl_new_tree()

        # set priority
        dc.sp.priority.v  = 1
        dc.sp.challenge.v = 1
        dc.sp.name.v = 'Unnamed'
        dc.sp.ptype.v = 'Application'
        dc.sp.category.v = 'Development'

        # init project attributes
        dc.sp.created.v     = timestamp
        dc.sp.modified.v    = timestamp

        # reset states
        applyStates(states.new_project, dc.ui.project.v)

        # init log control data
        dc.sp.nextlid.v     = 1
        dc.sp.log.index.v   = set()

        # set state
        applyStates(states.selected, dc.ui.project.v)
        projectlist.reloadTable()
        dc.ui.project.v.line_project_name.setFocus()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
        dc.r.changed.v = True
        projectlist.reloadTable()

'''
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onOpenClicked(self)', 'self')
    def onOpenClicked(self):
        if dc.r.changed.v:
            q = 'Discard changes?'
            m = 'Opening a file will discard your changes. ' \
                + 'Do you want to proceed?'
            yes, no = QMessageBox.Yes, QMessageBox.No
            response = QMessageBox.question(dc.ui.main.v, q, m, yes|no)
            if response == QMessageBox.StandardButton.No: return
        title  = 'Open nelia1 document'
        select = 'Nelia Files (*{})'.format(dc.x.extension.v)
        path = QFileDialog.getOpenFileName(
            dc.ui.main.v, title, dc.x.default.path.v, select)[0]
        if not path: return False
        result = dcload(path)
        if isinstance(result, Exception):
            title, message = 'open failed', 'open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            dc.x.path.v = None
            return
        dc.spid.v = 1
        self.reloadTable()
        dc.r.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onOpenLast(self)', 'self')
    def onOpenLast(self):
        result = dcload(dc.c.lastpath.v)
        if isinstance(result, Exception):
            title, message = 'Open failed', 'Open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        dc.spid.v = 1
        self.reloadTable()
        dc.r.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onSaveClicked(self)', 'self')
    def onSaveClicked(self):
        if not dc.x.path.v:
            t = 'Save nelia1 document'
            q = 'Nelia Files (*{})'.format(dc.x.extension.v)
            path = QFileDialog.getSaveFileName(
                dc.ui.main.v, t, dc.x.default.path.v, q)[0]
            if path == '': return
            extension_start = len(path) - len(dc.x.extension.v)
            if path.rfind(dc.x.extension.v) != extension_start:
                path += dc.x.extension.v
        else: path = dc.x.path.v
        result = dcsave(path)
        if isinstance(result, Exception):
            title, message = 'Save failed', 'Save failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        dc.ui.project.v.push_save.hide()
        self.view.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onDeleteProject(self)', 'self')
    def onDeleteProject(self):
        t = 'Delete project?'
        q = 'Sure you want to delete project {}: {}?'\
                .format(str(dc.spid.v), dc.sp.name.v)
        yes, no = QMessageBox.Yes, QMessageBox.No
        response = QMessageBox.question(dc.ui.project.v, t, q, yes|no)
        if response == QMessageBox.StandardButton.No: return
        dc.s.idx.pid.v.remove(dc.spid.v)
        del dc.s.__dict__['_{}'.format(dc.spid.v)]
        dc.spid.v = 0
        dc.r.changed.v = True
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''

