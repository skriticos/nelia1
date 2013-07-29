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
        'tbl_project_list'      : {'visible': True, 'enabled': False},
        'selected_project_group': {'visible': True, 'enabled': False},
        'line_selected_project' : {'text': 'No Project Selected'}
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Project list table headers
# This class handles the project list. It provides methods to initialize table
# and interact with items on it.

class NxProjectList:

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
        dc.x.project.view.v.setAlternatingRowColors(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxProject(QObject):

    @logger('NxProject.__init__(self)', 'self')
    def __init__(self):

        dc.spid.v = 0
        NxProjectList.initTable()

        # callbacks
        dc.ui.project.v.btn_project_new.clicked.connect(self.onNewProjectClicked)
        dc.ui.project.v.btn_info_max.toggled.connect(self.onInfoMaxToggled)
        NxProjectStates.applyStates(NxProjectStates.startup)

        """
        widget = dc.ui.project.v
        diag_new = self.diag_new = dc.ui.project_diag_new.v
        diag_edit = self.diag_edit = dc.ui.project_diag_edit.v
        widget.push_new.clicked.connect (self.onNewClicked)
        widget.push_edit.clicked.connect(self.showEditProject)
        diag_new.accepted.connect(self.onNewProject)
        diag_edit.accepted.connect(self.onEditProject)
        widget.push_delete.clicked.connect(self.onDeleteProject)
        widget.push_open.clicked.connect(self.onOpenClicked)
        widget.push_open_last.clicked.connect(self.onOpenLast)
        widget.push_save.clicked.connect(self.onSaveClicked)

        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        widget.text_description.textChanged.connect(self.onDescriptionChanged)
        self.view.activated.connect(self.showEditProject)
        if dc.c.lastpath.v: widget.push_open_last.show()
        else:               widget.push_open_last.hide()
        if dc.x.config.loaded.v:
            self.loadLayout()
        """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Maximize / restore callback for infox maximization toggle

    @logger('NxProject.onInfoMaxTogled(self, state)', 'self', 'state')
    def onInfoMaxToggled(self, state):
        if state:
            NxProjectStates.applyStates(NxProjectStates.description_maximized)
        else:
            NxProjectStates.applyStates(NxProjectStates.description_normal)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Create a new blanko project

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

        # init project attributes
        dc.sp.name.v        = ''
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

        # add new project to project list
        dc.x.project.model.v.insertRow(0, [
            QStandardItem(str(pid).zfill(4)),
            QStandardItem(dc.s._(pid).name.v),
            QStandardItem(dc.s._(pid).ptype.v),
            QStandardItem('{}.{}'.format(*dc.s._(pid).m.active.v)),
            QStandardItem(dc.s._(pid).category.v),
            QStandardItem(str(dc.s._(pid).priority.v)),
            QStandardItem(str(dc.s._(pid).challenge.v)),
            QStandardItem(convert(dc.s._(pid).modified.v)),
            QStandardItem(convert(dc.s._(pid).created.v)) ])

        # select new project
        index = dc.x.project.model.v.index(0, 0)
        s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
        dc.x.project.selection_model.v.clear()
        dc.x.project.selection_model.v.select(index, s|r)

        # set state
        NxProjectStates.applyStates(NxProjectStates.selected)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxLogger.onNewClicked(self)', 'self')
    def onNewClicked(self):
        diag = dc.ui.project_diag_new.v
        diag.line_name.clear()
        diag.combo_ptype.setCurrentIndex(0)
        diag.combo_status.setCurrentIndex(0)
        diag.combo_category.setCurrentIndex(0)
        diag.spin_priority.setValue(0)
        diag.spin_challenge.setValue(0)
        diag.text_description.clear()
        diag.line_name.setFocus()
        diag.show()
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
    @logger('NxProject.touchProject(self)', 'self')
    def touchProject(self):
        timestamp = int(time.time())
        dc.sp.modified.v = timestamp
        row = self.view.currentIndex().row()
        self.model.setItem(row, 8, QStandardItem(convert(timestamp)))
        dc.r.changed.v = True
        dc.ui.project.v.push_save.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onSelectionChanged(self, item_selection, previous)',
            'self', 'item_selection', 'previous')
    def onSelectionChanged(self, item_selection, previous):
        indexes = item_selection.indexes()
        if not indexes: return
        row = indexes[0].row()
        index = self.model.index(row, 0)
        dc.spid.v = int(self.model.itemFromIndex(index).text())
        dc.sp = dc.s._(dc.spid.v)
        for w in [dc.ui.project.v.text_description]:
            self.init = True
            w.setPlainText(dc.sp.description.v)
            self.init = False
            w.setEnabled(True)
        name = dc.sp.name.v
        dc.ui.main.v.setWindowTitle('Nelia1 - {}'.format(name))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onDescriptionChanged(self)', 'self')
    def onDescriptionChanged(self):
        if self.init: return
        dc.sp.description.v = dc.ui.project.v.text_description.toPlainText()
        self.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.saveLayout(self)', 'self')
    def saveLayout(self):
        dc.c.project.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.project.header.width.v.append(self.view.columnWidth(i))
        sort  = self.horizontal_header.sortIndicatorSection()
        order = self.horizontal_header.sortIndicatorOrder().__repr__()
        dc.c.project.sort.column.v = sort
        dc.c.project.sort.order.v  = order
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.loadLayout(self)', 'self')
    def loadLayout(self):
        for i,v in enumerate(dc.c.project.header.width.v):
            self.view.setColumnWidth(i, v)
        if dc.c.project.sort.column.v:
            self.horizontal_header.setSortIndicator(
                dc.c.project.sort.column.v, convert(dc.c.project.sort.order.v))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.reloadTable(self)', 'self')
    def reloadTable(self):
        self.init = True
        self.saveLayout()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        dc.ui.project.v.push_open_last.hide()
        if not dc.s.idx.pid.v:
            dc.ui.main.v.setWindowTitle('Nelia1')
        for pid in dc.s.idx.pid.v:
            major, minor = dc.s._(pid).m.active.v
            self.model.insertRow(0, [
                QStandardItem(str(pid).zfill(4)),
                QStandardItem(dc.s._(pid).name.v),
                QStandardItem(dc.s._(pid).status.v),
                QStandardItem(dc.s._(pid).ptype.v),
                QStandardItem('{}.{}'.format(major, minor)),
                QStandardItem(dc.s._(pid).category.v),
                QStandardItem(str(dc.s._(pid).priority.v)),
                QStandardItem(str(dc.s._(pid).challenge.v)),
                QStandardItem(convert(dc.s._(pid).modified.v)),
                QStandardItem(convert(dc.s._(pid).created.v)) ])
        self.loadLayout()
        if not dc.spid.v and len(dc.s.idx.pid.v):
            dc.spid.v = max(dc.s.idx.pid.v)
        for i in range(self.model.rowCount()):
            index = self.model.index(i, 0)
            pid = int(self.model.itemFromIndex(index).text())
            if pid == dc.spid.v:
                selmod = self.view.selectionModel()
                s, r = QItemSelectionModel.Select, QItemSelectionModel.Rows
                selmod.select(index, s|r)
                break
        w = dc.ui.project.v
        if len(dc.s.idx.pid.v):
            dc.m.main.v.enableTabs()
            w.push_edit.show()
            w.push_delete.show()
            if dc.r.changed.v: w.push_save.show()
            else:              w.push_save.hide()
            w.push_new.setDefault(False)
            self.view.setFocus()
        else:
            dc.r.changed.v = False
            w.text_description.clear()
            w.text_description.setEnabled(False)
            dc.m.main.v.dissableTabs()
            w.push_edit.hide()
            w.push_delete.hide()
            w.push_save.hide()
            w.push_new.setFocus()
        self.init = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onNewProject(self)', 'self')
    def onNewProject(self):
        name        = self.diag_new.line_name.text()
        category    = self.diag_new.combo_category.currentText()
        status      = self.diag_new.combo_status.currentText()
        ptype       = self.diag_new.combo_ptype.currentText()
        priority    = self.diag_new.spin_priority.value()
        challenge   = self.diag_new.spin_challenge.value()
        description = self.diag_new.text_description.toPlainText()
        self.createNewProject(name, category, status, ptype, priority,
                              challenge, description)
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.createNewProject(self, name, category, status, ptype, '
             + 'priority, challenge, description)',
            'self', 'name', 'category', 'status', 'ptype', 'priority',
            'challenge', 'description')
    def createNewProject(self, name, category, status, ptype, priority,
                         challenge, description):
        timestamp = int(time.time())
        pid = dc.s.nextpid.v
        dc.s.idx.pid.v.add(pid)
        dc.s.nextpid.v += 1
        dc.spid.v = pid
        dc.sp = dc.s._(pid)
        dc.sp.nextlid.v     = 1
        dc.sp.name.v        = name
        dc.sp.category.v    = category
        dc.sp.status.v      = status
        dc.sp.ptype.v       = ptype
        dc.sp.priority.v    = priority
        dc.sp.challenge.v   = challenge
        dc.sp.description.v = description
        dc.sp.created.v     = timestamp
        dc.sp.modified.v    = timestamp
        mistctrl_new_tree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.showEditProject(self)', 'self')
    def showEditProject(self):
        self.diag_edit.line_name.setText(dc.sp.name.v)
        i = self.diag_edit.combo_ptype.findText(dc.sp.ptype.v)
        self.diag_edit.combo_ptype.setCurrentIndex(i)
        i = self.diag_edit.combo_status.findText(dc.sp.status.v)
        self.diag_edit.combo_status.setCurrentIndex(i)
        i = self.diag_edit.combo_category.findText(dc.sp.category.v)
        self.diag_edit.combo_category.setCurrentIndex(i)
        self.diag_edit.spin_priority.setValue(dc.sp.priority.v)
        self.diag_edit.spin_challenge.setValue(dc.sp.challenge.v)
        self.diag_edit.text_description.setPlainText(dc.sp.description.v)
        self.diag_edit.show()
        self.diag_edit.line_name.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    @logger('NxProject.onEditProject(self)', 'self')
    def onEditProject(self):
        name        = self.diag_edit.line_name.text()
        category    = self.diag_edit.combo_category.currentText()
        status      = self.diag_edit.combo_status.currentText()
        ptype       = self.diag_edit.combo_ptype.currentText()
        priority    = self.diag_edit.spin_priority.value()
        challenge   = self.diag_edit.spin_challenge.value()
        description = self.diag_edit.text_description.toPlainText()
        self.editProject(name, category, status, ptype, priority, challenge,
                         description)
        self.touchProject()
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # this works on dc.sp (selected project)
    @logger('NxProject.editProject(self, name, category, status, ptype, '
             + 'priority, challenge, description)',
            'self', 'name', 'category', 'status', 'ptype', 'priority',
            'challenge', 'description')
    def editProject(self, name, category, status, ptype, priority, challenge,
            description):
        dc.sp.name.v        = name
        dc.sp.category.v    = category
        dc.sp.status.v      = status
        dc.sp.ptype.v       = ptype
        dc.sp.priority.v    = priority
        dc.sp.challenge.v   = challenge
        dc.sp.description.v = description
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

