# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, datetime, time
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from datastore import data, convert
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxProject:
    def __init__(self):
        data.spid = 0
        # show new project dialog
        dc.ui.project.v.push_new.clicked.connect(self.onNewClicked)
        # show edit project dialog
        dc.ui.project.v.push_edit.clicked.connect(self.showEditProject)
        dc.ui.project_diag_new.v.accepted.connect(self.onNewProject)
        dc.ui.project_diag_edit.v.accepted.connect(self.onEditProject)
        dc.ui.project.v.push_delete.clicked.connect(self.onDeleteProject)
        dc.ui.project.v.push_open.clicked.connect(self.onOpenClicked)
        dc.ui.project.v.push_open_last.clicked.connect(self.onOpenLast)
        dc.ui.project.v.push_save.clicked.connect(self.onSaveClicked)
        dc.ui.project.v.push_help.clicked.connect(
            dc.ui.project_diag_help.v.show)
        # setup table
        self.view = dc.ui.project.v.view
        self.view_headers = [
                'ID', 'Name', 'Status', 'Type', 'Verson', 'Category',
                'Priority', 'Challenge', 'Modified', 'Created' ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.view_headers)
        self.view.setModel(self.model)
        self.selection_model = self.view.selectionModel()
        self.horizontal_header = self.view.horizontalHeader()
        self.view.setAlternatingRowColors(True)
        self.diag_new = dc.ui.project_diag_new.v
        self.diag_edit = dc.ui.project_diag_edit.v
        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        dc.ui.project.v.text_description.textChanged.connect(
            self.onDescriptionChanged)
        self.view.activated.connect(self.showEditProject)
        # global handles for getting currently selected pid and updating
        # timestamp for currently selected project
        data.touchProject = self.touchProject
        self.reloadTable()
        if dc.c.lastpath.v: dc.ui.project.v.push_open_last.show()
        else:               dc.ui.project.v.push_open_last.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewClicked(self):
        dc.ui.project_diag_new.v.line_name.clear()
        dc.ui.project_diag_new.v.combo_ptype.setCurrentIndex(0)
        dc.ui.project_diag_new.v.combo_status.setCurrentIndex(0)
        dc.ui.project_diag_new.v.combo_category.setCurrentIndex(0)
        dc.ui.project_diag_new.v.spin_priority.setValue(0)
        dc.ui.project_diag_new.v.spin_challenge.setValue(0)
        dc.ui.project_diag_new.v.text_description.clear()
        dc.ui.project_diag_new.v.line_name.setFocus()
        dc.ui.project_diag_new.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onOpenClicked(self):
        # throw away changes?
        if data.run['changed']:
            response = QMessageBox.question(
                dc.ui.main.v, 'Discard changes?',
                'Opening a file will discard your changes. ' + \
                'Do you want to proceed?',
                QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.StandardButton.No: return
        # read path
        path = QFileDialog.getOpenFileName(
            dc.ui.main.v, 'Open nelia1 document', data.default_path,
            'Nelia Files (*{})'.format(data.extension))[0]
        # path dialog aborted
        if not path:
            return False
        # set path and save document
        result = data.open_document(path)
        if isinstance(result, Exception):
            title, message = 'open failed', 'open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            data.run['path'] = None
            return
        data.spid = 1
        self.reloadTable()
        data.run['changed'] = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onOpenLast(self):
        path = dc.c.lastpath.v
        result = data.open_document(path)
        if isinstance(result, Exception):
            title, message = 'Open failed', 'Open failed! ' + str(result)
            QMessageBox.critical(dc.ui.main.v, title, message)
            return
        data.spid = 1
        self.reloadTable()
        data.run['changed'] = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSaveClicked(self):
        if not data.run['path']:
            path = QFileDialog.getSaveFileName(
                dc.ui.main.v,
                'Save nelia1 document', data.default_path,
                'Nelia Files (*{})'.format(data.extension))[0]
            # dialog aborted?
            if path == '':
                return
            # extension check and optional appending
            extension_start = len(path) - len(data.extension)
            if path.rfind(data.extension) != extension_start:
                path += data.extension
        else: path = data.run['path']
        result = data.save_document(path)
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
        data.spro['modified'] = timestamp
        row = self.view.currentIndex().row()
        self.model.setItem(row, 8, QStandardItem(convert(timestamp)))
        data.run['changed'] = True
        dc.ui.project.v.push_save.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChanged(self, item_selection):
        # get indexes
        indexes = item_selection.indexes()
        # return if no indexes are selected
        if not indexes: return
        row = indexes[0].row()
        index = self.model.index(row, 0)
        data.spid = int(self.model.itemFromIndex(index).text())
        data.spro = data.project[data.spid]
        # update content and enable project description widget
        for w in [dc.ui.project.v.text_description]:
            w.setPlainText(data.spro['description'])
            w.setEnabled(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDescriptionChanged(self):
        if self.init: return
        data.spro['description'] =dc.ui.project.v.text_description.toPlainText()
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
        self.model.setHorizontalHeaderLabels(self.view_headers)
        # hide open last after first activity
        dc.ui.project.v.push_open_last.hide()
        # load project items into table
        for pid, project in data.project.items():
            if pid == 0: continue
            major, minor = data.project[pid]['meta']['current_milestone']
            self.model.insertRow(0, [
                QStandardItem(str(pid).zfill(4)),
                QStandardItem(project['name']),
                QStandardItem(project['status']),
                QStandardItem(project['ptype']),
                QStandardItem('{}.{}'.format(major,minor)),
                QStandardItem(project['category']),
                QStandardItem(str(project['priority'])),
                QStandardItem(str(project['challenge'])),
                QStandardItem(convert(project['modified'])),
                QStandardItem(convert(project['created']))
            ])
        # restore previous layout (sorting)
        self.loadLayout()
        # -- apply selection
        # if project was deleted, data.spid == 0, we want to select the last
        # project ID
        if not data.spid and len(data.project) > 1:
            data.spid = sorted(data.project.keys())[-1]
        for i in range(self.model.rowCount()):
            index = self.model.index(i, 0)
            pid = int(self.model.itemFromIndex(index).text())
            if pid == data.spid:
                selmod = self.view.selectionModel()
                selmod.select(index,
                    QItemSelectionModel.Select|QItemSelectionModel.Rows)
                break
        # set state of controls
        if len(data.project) > 1:
            dc.m.main.v.enableTabs()
            dc.ui.project.v.push_edit.show()
            dc.ui.project.v.push_delete.show()
            if data.run['changed']:
                dc.ui.project.v.push_save.show()
            else:
                dc.ui.project.v.push_save.hide()
            dc.ui.project.v.push_new.setDefault(False)
            self.view.setFocus()
        # last project deleted
        else:
            # don't want to save empty document
            data.run['changed'] = False
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
        pid = data.project[0]['next_pid']
        # create new project entry
        # meta: general project data
        # log: log data
        # milestone: versions, features, issues
        p = data.project[pid] = {
                'meta': {'next_lid': 1, 'next_miid': 1,
                         'current_milestone': (0,0)},
                'log': {},
                'milestone' : [
                    [{'description': '', 'm': '0.1',
                      'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}],
                    [{'description': '', 'm': '1.0',
                      'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
                    ],
                'mi_index' : {}}
        p['name']        = self.diag_new.line_name.text()
        p['category']    = self.diag_new.combo_category.currentText()
        p['status']      = self.diag_new.combo_status.currentText()
        p['ptype']       = self.diag_new.combo_ptype.currentText()
        p['priority']    = self.diag_new.spin_priority.value()
        p['challenge']   = self.diag_new.spin_challenge.value()
        p['description'] = self.diag_new.text_description.toPlainText()
        p['created']     = timestamp
        p['modified']    = timestamp
        data.project[0]['next_pid'] += 1
        data.spid = pid
        data.spro = data.project[data.spid]
        self.reloadTable()
        self.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def showEditProject(self):
        self.diag_edit.line_name.setText(data.spro['name'])
        self.diag_edit.combo_ptype.setCurrentIndex(
            self.diag_edit.combo_ptype.findText(data.spro['ptype']))
        self.diag_edit.combo_status.setCurrentIndex(
            self.diag_edit.combo_status.findText(data.spro['status']))
        self.diag_edit.combo_category.setCurrentIndex(
            self.diag_edit.combo_category.findText(data.spro['category']))
        self.diag_edit.spin_priority.setValue(data.spro['priority'])
        self.diag_edit.spin_challenge.setValue(data.spro['challenge'])
        self.diag_edit.text_description.setPlainText(data.spro['description'])
        self.diag_edit.show()
        self.diag_edit.line_name.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onEditProject(self):
        data.spro['name']        = self.diag_edit.line_name.text()
        data.spro['category']    = self.diag_edit.combo_category.currentText()
        data.spro['status']      = self.diag_edit.combo_status.currentText()
        data.spro['ptype']       = self.diag_edit.combo_ptype.currentText()
        data.spro['priority']    = self.diag_edit.spin_priority.value()
        data.spro['challenge']   = self.diag_edit.spin_challenge.value()
        data.spro['description'] = self.diag_edit.text_description.toPlainText()
        self.reloadTable()
        self.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDeleteProject(self):
        response = QMessageBox.question(
            dc.ui.project.v,
            'Delete project?',
            'Sure you want to delete project {}: {}?'.format(
                str(data.spid), data.spro['name']),
            QMessageBox.Yes|QMessageBox.No)
        if response == QMessageBox.StandardButton.No: return
        del data.project[data.spid]
        data.spid = 0
        # can't touch deleted project, direct changed update
        data.run['changed'] = True
        # reload table
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

