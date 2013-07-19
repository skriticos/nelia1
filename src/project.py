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
    @logger('NxProject.__init__(self)', 'self')
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
        timestamp = int(time.time())
        pid = dc.s.nextpid.v
        dc.s.idx.pid.v.add(pid)
        dc.s.nextpid.v += 1
        dc.spid.v = pid
        dc.sp = dc.s._(pid)
        dc.sp.nextlid.v     = 1
        dc.sp.nextmiid.v    = 1
        dc.sp.curr.major.v  = 0
        dc.sp.curr.minor.v  = 1
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
        dc.sp.m.idx.v = {0, 1}   # major milestone index
        dc.sp.m._(0).idx.v = {1} # minor milestone index (for 0.x)
        dc.sp.m._(1).idx.v = {0}
        self.reloadTable()
        self.touchProject()
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

