# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os, datetime, time
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datacore import *
from mistctrl import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project GUI state control
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# This class declares states. These states contain a list of widgets and the
# enabled attribute value.

class NxProjectStates:

    # Startup state. Can create new projects and load document.

    startup = {
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
        'sb_project_priority'   : {'value': 0},
        'sb_project_challenge'  : {'value': 0}
    }

    # New project state

    new_project = {
        'line_selected_project' : {'text': 'Unnamed'},
        'line_project_name'     : {'text': 'Unnamed'},
        'cb_project_type'       : {'index': 0},
        'cb_project_category'   : {'index': 0},
        'sb_project_priority'   : {'value': 0},
        'sb_project_challenge'  : {'value': 0},
        'text_project_info'     : {'clear': True}
    }

    # If the loaded configuration contains the path to a last saved document,
    # enable this control. Sub-state to startup. Is disaled once a project is
    # selected.

    last = {
        'btn_doc_open_last'     : {'visible': True, 'enabled': True},
    }

    # Once a project is created or a document is loaded (wich implies a selected
    # project), the project controls are enabled and the document can be saved.

    selected = {
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

    # maximize / restore state for project description

    description_normal = {
        'project_meta': {'visible': True, 'enabled': True},
        'project_list': {'visible': True, 'enabled': True},
        'gl_info':      {'margins': (0, 0, 0, 0)}
    }

    description_maximized = {
        'project_meta': {'visible': False, 'enabled': True},
        'project_list': {'visible': False, 'enabled': True},
        'gl_info':      {'margins': (0, 0, 15, 0)}
    }


    # This simply goes through the list of controls in the states dictionary and
    # applies the assigned states on the project widget.

    @logger('NxProjectStates.applyStates(states, hide=False)', 'states')
    def applyStates(states, hide=False):

        # loop through controls (widgets)
        for control, state in states.items():

            # loop through state attributes
            if 'enabled' in state:
                dc.ui.project.v.__dict__[control].setEnabled(state['enabled'])
            if 'visible' in state:
                dc.ui.project.v.__dict__[control].setVisible(state['visible'])
            if 'margins' in state:
                dc.ui.project.v.__dict__[control] \
                        .setContentsMargins(*state['margins'])
            if 'text' in state:
                dc.ui.project.v.__dict__[control].setText(state['text'])
            if 'clear' in state:
                dc.ui.project.v.__dict__[control].clear()
            if 'index' in state:
                dc.ui.project.v.__dict__[control] \
                        .setCurrentIndex(state['index'])
            if 'value' in state:
                dc.ui.project.v.__dict__[control].setValue(state['value'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project list control class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Project list table headers
# This class handles the project list. It provides methods to initialize table
# and interact with items on it.

class NxProjectList:

    colPid       = 0
    colName      = 1
    colType      = 2
    colVersion   = 3
    colCategory  = 4
    colPritoriy  = 5
    colChallenge = 6
    colModified  = 7
    colCreated   = 8

    # Project list header labels.
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

    @logger('NxProjectList.initTable()')
    def initTable():
        dc.x.project.view.v \
                = dc.ui.project.v.tbl_project_list
        dc.x.project.model.v \
                = QStandardItemModel()
        dc.x.project.model.v.setHorizontalHeaderLabels(NxProjectList.headers)
        dc.x.project.view.v.setModel(dc.x.project.model.v)
        dc.x.project.selection_model.v \
                = dc.x.project.view.v.selectionModel()
        dc.x.project.horizontal_header.v \
                = dc.x.project.view.v.horizontalHeader()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# layout / reload table
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @logger('NxProjectList.saveLayout(self)')
    def saveLayout():

        dc.c.project.header.width.v = list()
        for i in range(dc.x.project.model.v.columnCount()):
            dc.c.project.header.width.v.append(
                    dc.x.project.view.v.columnWidth(i))
        sort  = dc.x.project.horizontal_header.v.sortIndicatorSection()
        order = dc.x.project.horizontal_header.v.sortIndicatorOrder().__repr__()
        dc.c.project.sort.column.v = sort
        dc.c.project.sort.order.v  = order

    @logger('NxProjectList.loadLayout(self)')
    def loadLayout():

        for i,v in enumerate(dc.c.project.header.width.v):
            dc.x.project.view.v.setColumnWidth(i, v)
        if dc.c.project.sort.column.v:
            dc.x.project.horizontal_header.v.setSortIndicator(
                dc.c.project.sort.column.v, convert(dc.c.project.sort.order.v))


    # Reloads the project list table.
    # The toggled attribute is sent by the filter callbacks and is ignored.
    @logger('NxProjectList.reloadTable(toggled=False)')
    def reloadTable(toggled=False):

        NxProjectList.saveLayout()

        # clear table
        dc.x.project.model.v.clear()
        dc.x.project.model.v.setHorizontalHeaderLabels(NxProjectList.headers)

        # reload table
        for pid in dc.s.index.pid.v:

            priority  = dc.s._(pid).priority.v
            challenge = dc.s._(pid).challenge.v

            priolist = set()
            if dc.ui.project.v.btn_prio_low.isChecked():
                priolist.add(1)
                priolist.add(2)
                priolist.add(3)
            if dc.ui.project.v.btn_prio_medium.isChecked():
                priolist.add(4)
                priolist.add(5)
                priolist.add(6)
            if dc.ui.project.v.btn_prio_high.isChecked():
                priolist.add(7)
                priolist.add(8)
                priolist.add(9)
            challengelist = set()
            if dc.ui.project.v.btn_challenge_low.isChecked():
                challengelist.add(1)
                challengelist.add(2)
                challengelist.add(3)
            if dc.ui.project.v.btn_challenge_medium.isChecked():
                challengelist.add(4)
                challengelist.add(5)
                challengelist.add(6)
            if dc.ui.project.v.btn_challenge_hard.isChecked():
                challengelist.add(7)
                challengelist.add(8)
                challengelist.add(9)

            if priority not in priolist:
                dc.spid.v = 0
                dc.sp = None
                continue
            if challenge not in challengelist:
                dc.spid.v = 0
                dc.sp = None
                continue

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

        NxProjectList.loadLayout()

        # set selection
        dc.x.project.selection_model.v.reset()
        if dc.spid.v:

            # iterate through table rows
            for rowcnt in range(dc.x.project.model.v.rowCount()):
                index = dc.x.project.model.v.index(rowcnt, 0)
                pid = int(dc.x.project.model.v.data(index))

                # if we have a match, select it and abort
                if pid == dc.spid.v:
                    s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                    dc.x.project.selection_model.v.setCurrentIndex(index, s|r)
                    break

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Main project control class
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class NxProject(QObject):

    @logger('NxProject.__init__(self)', 'self')
    def __init__(self):

        # setup callbacks
        dc.ui.project.v.btn_project_new.clicked \
                .connect(self.onNewProjectClicked)
        dc.ui.project.v.btn_info_max.toggled \
                .connect(self.onInfoMaxToggled)
        dc.ui.project.v.btn_project_sort_modified.clicked \
                .connect(self.onSortProjectList)

        # filter callbacks
        dc.ui.project.v.btn_prio_low.toggled \
                .connect(NxProjectList.reloadTable)
        dc.ui.project.v.btn_prio_medium.toggled \
                .connect(NxProjectList.reloadTable)
        dc.ui.project.v.btn_prio_high.toggled \
                .connect(NxProjectList.reloadTable)
        dc.ui.project.v.btn_challenge_low.toggled \
                .connect(NxProjectList.reloadTable)
        dc.ui.project.v.btn_challenge_medium.toggled \
                .connect(NxProjectList.reloadTable)
        dc.ui.project.v.btn_challenge_hard.toggled \
                .connect(NxProjectList.reloadTable)

        # apply state
        dc.spid.v = 0
        NxProjectList.initTable()
        NxProjectStates.applyStates(NxProjectStates.startup)
        self.setEditCallbackState(True)
        if dc.x.config.loaded.v:
            NxProjectList.loadLayout()
            if dc.c.lastpath.v:
                NxProjectStates.applyStates(NxProjectStates.last)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Helpers
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Sets the cell content of the currently selected row in the project table.
    # Used by the selected project attribute change callbacks.

    @logger('NxProject.setTableValue(self, col, value)', 'self', 'col', 'value')
    def setTableValue(self, col, value):
        row = dc.x.project.selection_model.v.currentIndex().row()
        dc.x.project.model.v.setItem(row, col, QStandardItem(value))


    # Enable / disable the callbacks for the edit controls / selection during
    # programatic UI updates - mostly to avoid infinite loops and weird state
    # changes.

    @logger('NxProject.setEditCallbackState(self, state)', 'self', 'state')
    def setEditCallbackState(self, state):
        if state:
            dc.ui.project.v.line_project_name.textChanged \
                    .connect(self.onProjectNameChanged)
            dc.ui.project.v.cb_project_type.currentIndexChanged[str] \
                    .connect(self.onProjectTypeChanged)
            dc.ui.project.v.cb_project_category.currentIndexChanged[str] \
                    .connect(self.onProjectCategoryChanged)
            dc.ui.project.v.sb_project_priority.valueChanged[int] \
                    .connect(self.onProjectPriorityChanged)
            dc.ui.project.v.sb_project_challenge.valueChanged[int] \
                    .connect(self.onProjectChallengeChanged)
            dc.ui.project.v.text_project_info.textChanged \
                    .connect(self.onProjectDescriptionChanged)
            dc.x.project.selection_model.v.selectionChanged \
                    .connect(self.onSelectionChanged)
        else:
            dc.ui.project.v.line_project_name.textChanged \
                    .disconnect(self.onProjectNameChanged)
            dc.ui.project.v.cb_project_type.currentIndexChanged[str] \
                    .disconnect(self.onProjectTypeChanged)
            dc.ui.project.v.cb_project_category.currentIndexChanged[str] \
                    .disconnect(self.onProjectCategoryChanged)
            dc.ui.project.v.sb_project_priority.valueChanged[int] \
                    .disconnect(self.onProjectPriorityChanged)
            dc.ui.project.v.sb_project_challenge.valueChanged[int] \
                    .disconnect(self.onProjectChallengeChanged)
            dc.ui.project.v.text_project_info.textChanged \
                    .disconnect(self.onProjectDescriptionChanged)
            dc.x.project.selection_model.v.selectionChanged \
                    .disconnect(self.onSelectionChanged)


    # Updates the project modification date in the project table and sets the
    # changed value. This is called by all persistent data operations of the
    # document.

    @logger('NxProject.touchProject(self)', 'self')
    def touchProject(self):
        timestamp = int(time.time())
        dc.sp.modified.v = timestamp
        self.setTableValue(NxProjectList.colModified, convert(timestamp))
        dc.r.changed.v = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Read only callbacks (GUI only)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Maximize / restore callback for infox maximization toggle.

    @logger('NxProject.onInfoMaxTogled(self, state)', 'self', 'state')
    def onInfoMaxToggled(self, state):
        if state:
            NxProjectStates.applyStates(NxProjectStates.description_maximized)
        else:
            NxProjectStates.applyStates(NxProjectStates.description_normal)


    # Sort by modification date when control is clicked.

    @logger('NxProject.onSortProjectList(self)', 'self')
    def onSortProjectList(self):
            dc.x.project.horizontal_header.v.setSortIndicator(
                    NxProjectList.colModified,
                    PySide.QtCore.Qt.SortOrder.DescendingOrder)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Runtime change only callbacks (dc.spid / dc.sp = xx)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # Selected project changed -> update selected project edit controls and
    # selected project label. Update selected project runtime data.

    @logger('NxProject.onSelectionChanged(self, new, old)',
            'self', 'new', 'old')
    def onSelectionChanged(self, new, old):

        # check for valid index
        indexes = new.indexes()
        if not indexes:
            return

        # get selected pid from table model
        index = indexes[0]
        dc.spid.v = int(dc.x.project.model.v.itemFromIndex(index).text())
        dc.sp = dc.s._(dc.spid.v)

        # populate edit fields on selection change
        self.setEditCallbackState(False)
        dc.ui.project.v.line_project_name.setText(dc.sp.name.v)
        dc.ui.project.v.line_selected_project.setText(dc.sp.name.v)
        dc.ui.project.v.sb_project_priority.setValue(dc.sp.priority.v)
        dc.ui.project.v.sb_project_challenge.setValue(dc.sp.challenge.v)
        dc.ui.project.v.cb_project_type.setCurrentIndex(
                dc.ui.project.v.cb_project_type.findText(dc.sp.ptype.v))
        dc.ui.project.v.cb_project_category.setCurrentIndex(
                dc.ui.project.v.cb_project_category.findText(dc.sp.category.v))
        dc.ui.project.v.text_project_info.setText(dc.sp.description.v)
        self.setEditCallbackState(True)

        # set title
        dc.ui.main.v.setWindowTitle('Nelia1 - {}'.format(dc.sp.name.v))
        self.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Callbacks for selected project edit fields
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    @logger('NxProject.onProjectNameChanged(self, name)', 'self', 'name')
    def onProjectNameChanged(self, name):

        dc.sp.name.v = name
        dc.ui.project.v.line_selected_project.setText(name)
        self.touchProject()
        # Setting the project cell individually sometimes stops working for no
        # apparent reason. Reloading the table each time fixes the issue.
        self.setEditCallbackState(False)
        NxProjectList.reloadTable()
        self.setEditCallbackState(True)


    @logger('NxProject.onProjectTypeChanged(self, ptype)', 'self', 'ptype')
    def onProjectTypeChanged(self, ptype):

        dc.sp.ptype.v = ptype
        self.touchProject()
        self.setEditCallbackState(False)
        NxProjectList.reloadTable()
        self.setEditCallbackState(True)


    @logger('NxProject.onProjectCategoryChanged(self, category)',
            'self', 'category')
    def onProjectCategoryChanged(self, category):

        dc.sp.category.v = category
        self.touchProject()
        self.setEditCallbackState(False)
        NxProjectList.reloadTable()
        self.setEditCallbackState(True)


    @logger('NxProject.onProjectPriorityChanged(self, priority)',
            'self', 'priority')
    def onProjectPriorityChanged(self, priority):

        dc.sp.priority.v = priority
        self.touchProject()
        self.setEditCallbackState(False)
        NxProjectList.reloadTable()
        self.setEditCallbackState(True)


    @logger('NxProject.onProjectChallengeChanged(self, challenge)',
            'self', 'challenge')
    def onProjectChallengeChanged(self, challenge):

        dc.sp.challenge.v = challenge
        self.touchProject()
        self.setEditCallbackState(False)
        NxProjectList.reloadTable()
        self.setEditCallbackState(True)


    @logger('NxProject.onProjectDescriptionChanged(self)', 'self')
    def onProjectDescriptionChanged(self):

        dc.sp.description.v = dc.ui.project.v.text_project_info.toHtml()
        self.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create a new blanko project

    @logger('NxProject.onNewProjectClicked(self)', 'self')
    def onNewProjectClicked(self):

        # prepare
        timestamp = int(time.time())
        pid = dc.s.nextpid.v

        # reset states
        self.setEditCallbackState(False)
        NxProjectStates.applyStates(NxProjectStates.new_project)

        # init project control data
        dc.s.index.pid.v.add(pid)
        dc.s.nextpid.v += 1
        dc.spid.v = pid
        dc.sp = dc.s._(pid)

        # init project attributes
        dc.sp.name.v        = 'Unnamed'
        dc.sp.ptype.v       = dc.ui.project.v.cb_project_type.currentText()
        dc.sp.category.v    = dc.ui.project.v.cb_project_category.currentText()
        dc.sp.priority.v    = dc.ui.project.v.sb_project_priority.value()
        dc.sp.challenge.v   = dc.ui.project.v.sb_project_challenge.value()
        dc.sp.description.v = ''
        dc.sp.created.v     = timestamp
        dc.sp.modified.v    = timestamp

        # init log control data
        dc.sp.nextlid.v     = 1

        # init milestone control data
        mistctrl_new_tree()

        NxProjectList.reloadTable()
        self.setEditCallbackState(True)

        # set state
        NxProjectStates.applyStates(NxProjectStates.selected)

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

