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
# Project list table headers
class NxProjectList:
    headers =  [
        'ID', 'Name', 'Type', 'Verson', 'Category', 'Priority',
        'Challenge', 'Modified', 'Created' ]
    def initTable():
        dc.x.project.view.v = dc.ui.project.v.tbl_project_list
        dc.x.project.model.v = QStandardItemModel()
        dc.x.project.model.v.setHorizontalHeaderLabels(NxProjectList.headers)
        dc.x.project.view.v.setModel(dc.x.project.model.v)
        dc.x.project.selection_model.v = dc.x.project.view.v.selectionModel()
        dc.x.project.horizontal_header.v \
                = dc.x.project.view.v.horizontalHeader()
        dc.x.project.view.v.setAlternatingRowColors(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This class declares states. These states contain a list of widgets and the
# enabled attribute value.
class NxProjectStates:
    # Startup state. Can create new projects and load document.
    startup = {
        'btn_doc_new': False,
        'btn_doc_open': True,
        'btn_doc_open_last': False,
        'btn_doc_save_as': False,
        'btn_project_delete': False,
        'btn_project_new': True,
        'btn_show_roadmap': False,
        'btn_show_logs': False,
        'selected_project_group': False
    }
    # If the loaded configuration contains the path to a last saved document,
    # enable this control. Sub-state to startup. Is disaled once a project is
    # selected.
    last = {
        'btn_doc_open_last': True
    }
    # Once a project is created or a document is loaded (wich implies a selected
    # project), the project controls are enabled and the document can be saved.
    selected = {
        'btn_doc_new': True,
        'btn_doc_open': True,
        'btn_doc_open_last': False,
        'btn_doc_save_as': True,
        'btn_project_delete': True,
        'btn_project_new': True,
        'btn_show_roadmap': True,
        'btn_show_logs': True,
        'selected_project_group': True
    }
    # This simply goes through the list of controls in the states dictionary and
    # applies the assigned states on the project widget.
    @logger('NxProjectStates.applyStates(states)', 'states')
    def applyStates(states):
        for control, state in states.items():
            dc.ui.project.v.__dict__[control].setEnabled(state)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxProject:
    @logger('NxProject.__init__(self)', 'self')
    def __init__(self):
        dc.spid.v = 0
        NxProjectList.initTable()
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
        NxProjectStates.applyStates(NxProjectStates.startup)
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

