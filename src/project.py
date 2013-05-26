# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, datetime, time
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
headers =  [
    'ID', 'Name', 'Status', 'Type', 'Verson', 'Category', 'Priority',
    'Challenge', 'Modified', 'Created' ]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxProject:
    def __init__(self):
        dc.spid.v = 0
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
        widget.push_help.clicked.connect(dc.ui.project_diag_help.v.show)
        self.view = widget.view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.view.setModel(self.model)
        self.selection_model = self.view.selectionModel()
        self.horizontal_header = self.view.horizontalHeader()
        self.view.setAlternatingRowColors(True)
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        widget.text_description.textChanged.connect(self.onDescriptionChanged)
        self.view.activated.connect(self.showEditProject)
        self.reloadTable()
        if dc.c.lastpath.v: widget.push_open_last.show()
        else:               widget.push_open_last.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            dc.r.path.v = None
            return
        dc.spid.v = 1
        self.reloadTable()
        dc.r.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
    def onSaveClicked(self):
        if not dc.r.path.v:
            t = 'Save nelia1 document'
            q = 'Nelia Files (*{})'.format(dc.x.extension.v)
            path = QFileDialog.getSaveFileName(
                dc.ui.main.v, t, dc.x.default.path.v, q)[0]
            if path == '': return
            extension_start = len(path) - len(dc.x.extension.v)
            if path.rfind(dc.x.extension.v) != extension_start:
                path += dc.x.extension.v
        else: path = dc.r.path.v
        result = dcsave(path)
        if isinstance(result, Exception):
            title, message = 'Save failed', 'Save failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        dc.ui.project.v.push_save.hide()
        self.view.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def touchProject(self):
        """
        On project change (e.g. edit meta, add log or change roadmap),
        this should be called with the timestamp. It will update the last
        changed timestamp and update the project index display and mark
        changes as true.
        """
        timestamp = int(time.time())
        dc.sp.modified.v = timestamp
        row = self.view.currentIndex().row()
        self.model.setItem(row, 8, QStandardItem(convert(timestamp)))
        dc.r.changed.v = True
        dc.ui.project.v.push_save.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChanged(self, item_selection):
        # get indexes
        indexes = item_selection.indexes()
        # return if no indexes are selected
        if not indexes: return
        row = indexes[0].row()
        index = self.model.index(row, 0)
        dc.spid.v = int(self.model.itemFromIndex(index).text())
        dc.sp = dc.s._(dc.spid.v)
        # update content and enable project description widget
        for w in [dc.ui.project.v.text_description]:
            w.setPlainText(dc.sp.description.v)
            w.setEnabled(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDescriptionChanged(self):
        if self.init: return
        dc.sp.description.v =dc.ui.project.v.text_description.toPlainText()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        dc.c.project.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.project.header.width.v.append(self.view.columnWidth(i))
        dc.c.project.sort.column.v \
                = self.horizontal_header.sortIndicatorSection()
        dc.c.project.sort.order.v \
                = self.horizontal_header.sortIndicatorOrder().__repr__()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(dc.c.project.header.width.v):
            self.view.setColumnWidth(i, v)
        if dc.c.project.sort.column.v:
            self.horizontal_header.setSortIndicator(
                dc.c.project.sort.column.v, convert(dc.c.project.sort.order.v))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self):
        self.init = True
        self.saveLayout()
        # clean out data
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        # hide open last after first activity
        dc.ui.project.v.push_open_last.hide()
        # load project items into table
        for pid in dc.s.idx.pid.v:
            major, minor = dc.s._(pid).curr.major.v, dc.s._(pid).curr.minor.v
            self.model.insertRow(0, [
                QStandardItem(str(pid).zfill(4)),
                QStandardItem(dc.s._(pid).name.v),
                QStandardItem(dc.s._(pid).status.v),
                QStandardItem(dc.s._(pid).ptype.v),
                QStandardItem('{}.{}'.format(major,minor)),
                QStandardItem(dc.s._(pid).category.v),
                QStandardItem(str(dc.s._(pid).priority.v)),
                QStandardItem(str(dc.s._(pid).challenge.v)),
                QStandardItem(convert(dc.s._(pid).modified.v)),
                QStandardItem(convert(dc.s._(pid).created.v))
            ])
        # restore previous layout (sorting)
        self.loadLayout()
        # -- apply selection
        # if project was deleted, dc.spid.v == 0, we want to select the last
        # project ID
        if not dc.spid.v and len(dc.s.idx.pid.v):
            dc.spid.v = max(dc.s.idx.pid.v)
        for i in range(self.model.rowCount()):
            index = self.model.index(i, 0)
            pid = int(self.model.itemFromIndex(index).text())
            if pid == dc.spid.v:
                selmod = self.view.selectionModel()
                selmod.select(index,
                    QItemSelectionModel.Select|QItemSelectionModel.Rows)
                break
        # set state of controls
        if len(dc.s.idx.pid.v):
            dc.m.main.v.enableTabs()
            dc.ui.project.v.push_edit.show()
            dc.ui.project.v.push_delete.show()
            if dc.r.changed.v:
                dc.ui.project.v.push_save.show()
            else:
                dc.ui.project.v.push_save.hide()
            dc.ui.project.v.push_new.setDefault(False)
            self.view.setFocus()
        # last project deleted
        else:
            # don't want to save empty document
            dc.r.changed.v = False
            # set default state
            dc.ui.project.v.text_description.clear()
            dc.ui.project.v.text_description.setEnabled(False)
            dc.m.main.v.dissableTabs()
            dc.ui.project.v.push_edit.hide()
            dc.ui.project.v.push_delete.hide()
            dc.ui.project.v.push_save.hide()
            dc.ui.project.v.push_new.setFocus()
        self.init = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewProject(self):
        timestamp = int(time.time())
        pid = dc.s.nextpid.v
        dc.s.idx.pid.v.add(pid)
        dc.s.nextpid.v += 1
        dc.spid.v = pid
        dc.sp = dc.s._(pid)
        dc.sp.nextlid.v     = 1
        dc.sp.nextmiid.v    = 1
        dc.sp.curr.major.v  = 0
        dc.sp.curr.minor.v  = 0
        dc.sp.name.v        = self.diag_new.line_name.text()
        dc.sp.category.v    = self.diag_new.combo_category.currentText()
        dc.sp.status.v      = self.diag_new.combo_status.currentText()
        dc.sp.ptype.v       = self.diag_new.combo_ptype.currentText()
        dc.sp.priority.v    = self.diag_new.spin_priority.value()
        dc.sp.challenge.v   = self.diag_new.spin_challenge.value()
        dc.sp.description.v = self.diag_new.text_description.toPlainText()
        dc.sp.created.v     = timestamp
        dc.sp.modified.v    = timestamp
        dc.sp.midx.v = {} # dict with item id's and position id -> x, y
        dc.sp.m._(0)._(1).description.v = ''
        dc.sp.m._(0)._(1).idx.v = set()
        dc.sp.m._(1)._(0).description.v = ''
        dc.sp.m._(1)._(0).idx.v = set()
        dc.sp.m.idx.v = {0, 1} # major milestone index
        dc.sp.m._(0).idx.v = {1} # minor milestone index (for 0.x)
        dc.sp.m._(1).idx.v = {0}
        self.reloadTable()
        self.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def showEditProject(self):
        self.diag_edit.line_name.setText(dc.sp.name.v)
        self.diag_edit.combo_ptype.setCurrentIndex(
            self.diag_edit.combo_ptype.findText(dc.sp.ptype.v))
        self.diag_edit.combo_status.setCurrentIndex(
            self.diag_edit.combo_status.findText(dc.sp.status.v))
        self.diag_edit.combo_category.setCurrentIndex(
            self.diag_edit.combo_category.findText(dc.sp.category.v))
        self.diag_edit.spin_priority.setValue(dc.sp.priority.v)
        self.diag_edit.spin_challenge.setValue(dc.sp.challenge.v)
        self.diag_edit.text_description.setPlainText(dc.sp.description.v)
        self.diag_edit.show()
        self.diag_edit.line_name.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onEditProject(self):
        dc.sp.name.v        = self.diag_edit.line_name.text()
        dc.sp.category.v    = self.diag_edit.combo_category.currentText()
        dc.sp.status.v      = self.diag_edit.combo_status.currentText()
        dc.sp.ptype.v       = self.diag_edit.combo_ptype.currentText()
        dc.sp.priority.v    = self.diag_edit.spin_priority.value()
        dc.sp.challenge.v   = self.diag_edit.spin_challenge.value()
        dc.sp.description.v = self.diag_edit.text_description.toPlainText()
        self.reloadTable()
        self.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDeleteProject(self):
        response = QMessageBox.question(
            dc.ui.project.v,
            'Delete project?',
            'Sure you want to delete project {}: {}?'.format(
                str(dc.spid.v), dc.sp.name.v),
            QMessageBox.Yes|QMessageBox.No)
        if response == QMessageBox.StandardButton.No: return
        dc.s.idx.pid.v.remove(dc.spid.v)
        del dc.s.__dict__['_{}'.format(dc.spid.v)]
        dc.spid.v = 0
        dc.r.changed.v = True
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

