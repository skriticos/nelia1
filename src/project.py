# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import os, datetime, time
from datastore import data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxProject:

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):

        # show new project dialog
        data.w_project.push_new.clicked.connect(
            lambda: (
            data.w_project_diag_new.line_name.clear(),
            data.w_project_diag_new.combo_ptype.setCurrentIndex(0),
            data.w_project_diag_new.combo_status.setCurrentIndex(0),
            data.w_project_diag_new.combo_category.setCurrentIndex(0),
            data.w_project_diag_new.spin_priority.setValue(0),
            data.w_project_diag_new.spin_challenge.setValue(0),
            data.w_project_diag_new.text_description.clear(),
            data.w_project_diag_new.line_name.setFocus(),
            data.w_project_diag_new.show()))

        # show edit project dialog
        data.w_project.push_edit.clicked.connect(self.showEditProject)

        data.w_project_diag_new.accepted.connect(self.onNewProject)
        data.w_project_diag_edit.accepted.connect(
            self.onEditProject)
        data.w_project.push_delete.clicked.connect(self.onDeleteProject)

        data.w_project.push_open.clicked.connect(self.onOpenClicked)
        if 'lastpath' in data.c_config.config_data['datastore']:
            data.w_project.push_open_last.setEnabled(True)
        data.w_project.push_open_last.clicked.connect(self.onOpenLast)
        data.w_project.push_save.clicked.connect(self.onSaveClicked)
        data.w_project.push_help.clicked.connect(
            data.w_project_diag_help.show)

        # setup table
        self.table = data.w_project.table_project_list
        self.table_headers = [
                'ID', 'Name', 'Status', 'Type', 'Verson', 'Category',
                'Priority', 'Challenge', 'Modified', 'Created' ]
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.table_headers)
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        self.table.setAlternatingRowColors(True)

        self.diag_new = data.w_project_diag_new
        self.diag_edit = data.w_project_diag_edit

        self.selection_model.selectionChanged.connect(self.onSelectionChanged)
        data.w_project.text_description.textChanged.connect(
            self.onDescriptionChange)

        self.table.activated.connect(self.showEditProject)

        # global handles for getting currently selected pid and updating
        # timestamp for currently selected project
        data.getPid = self.getPid
        data.touchProject = self.touchProject

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onOpenClicked(self):
        # throw away changes?
        if data.run['changed']:
            response = QMessageBox.question(
                data.w_main, 'Discard changes?',
                'Opening a file will discard your changes. ' + \
                'Do you want to proceed?',
                QMessageBox.Yes|QMessageBox.No)
            if response == QMessageBox.StandardButton.No: return
        # read path
        path = QFileDialog.getOpenFileName(
            data.w_main, 'Open nelia1 document', data.default_path,
            'Nelia Files (*{})'.format(data.extension))[0]
        # path dialog aborted
        if not path:
            return False
        # set path and save document
        result = data.open_document(path)
        if isinstance(result, Exception):
            title, message = 'open failed', 'open failed! ' + str(result)
            QMessageBox.critical(data.w_main, title, message)
            data.run['path'] = None
            return
        self.reset()
        data.w_project.push_save.setEnabled(False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onOpenLast(self):
        path = data.c_config.config_data['datastore']['lastpath']
        result = data.open_document(path)
        if isinstance(result, Exception):
            title, message = 'Open failed', 'Open failed! ' + str(result)
            QMessageBox.critical(data.w_main, title, message)
            return
        self.reset()
        data.w_project.push_open_last.setEnabled(False)
        data.w_project.push_save.setEnabled(False)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSaveClicked(self):
        if not data.run['path']:
            path = QFileDialog.getSaveFileName(
                data.w_main,
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
            QMessageBox.critical(data.w_main, title, message)
            return
        data.w_project.push_save.setEnabled(False)
        self.table.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def touchProject(self, timestamp):
        """
        On project change (e.g. edit meta, add log or change roadmap),
        this should be called with the timestamp. It will update the last
        changed timestamp and update the project index display and mark
        changes as true.
        """
        data.project[self.getPid()]['modified'] = timestamp
        self.model.setItem(self.getActiveRow(), 8,
            QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()))
        data.run['changed'] = True
        data.w_project.push_save.setEnabled(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getPid(self):

        if not self.init:
            if self.table.currentIndex().row() == -1:
                return 0
            return int(self.model.itemFromIndex(
                    self.model.index(self.table.currentIndex().row(), 0)).text())


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getSelectedProjectName(self):

        return self.model.itemFromIndex(
                self.model.index(self.table.currentIndex().row(), 1)).text()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getActiveRow(self):

        return self.table.currentIndex().row()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChanged(self):

        if not self.init:
            pid = self.getPid()
            if data.project[0]['next_id'] > 1 and pid != 0:
                data.w_project.text_description.setEnabled(True)
                data.w_project.text_description.setPlainText(
                    data.project[pid]['description']
                )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDescriptionChange(self):

        data.project[self.getPid()]['description'] = \
                data.w_project.text_description.toPlainText()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):

        self.header_width = []
        for i in range(10):
            self.header_width.append(self.table.columnWidth(i))
        if self.horizontal_header.sortIndicatorSection() < 10:
            self.sort_column = self.horizontal_header.sortIndicatorSection()
            self.sort_order = self.horizontal_header.sortIndicatorOrder()
        else:
            self.sort_column = -1
            self.sort_order = None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):

        for i,v in enumerate(self.header_width):
            self.table.setColumnWidth(i, v)
        if self.sort_column != -1:
            self.horizontal_header.setSortIndicator(self.sort_column, self.sort_order)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self, state=None, preserveLayout=True):

        self.init = True

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.table_headers)

        for pid, project in data.project.items():
            if pid == 0: continue
            major, minor = data.project[pid]['meta']['current_milestone']
            disptime1 = datetime.datetime.fromtimestamp(project['modified']).isoformat()
            disptime2 = datetime.datetime.fromtimestamp(project['created']).isoformat()
            self.model.insertRow(0, [
                QStandardItem(str(pid).zfill(4)),
                QStandardItem(project['name']),
                QStandardItem(project['status']),
                QStandardItem(project['ptype']),
                QStandardItem('{}.{}'.format(major,minor)),
                QStandardItem(project['category']),
                QStandardItem(str(project['priority'])),
                QStandardItem(str(project['challenge'])),
                QStandardItem(disptime1),
                QStandardItem(disptime2),
            ])

        self.table.sortByColumn(8, Qt.DescendingOrder)

        if preserveLayout:
            self.loadLayout()

        self.init = False

        if len(data.project) > 1:

            self.table.selectRow(0)

            data.c_main.enableTabs()
            data.w_project.push_edit.setEnabled(True)
            data.w_project.push_delete.setEnabled(True)
            data.w_project.push_save.setEnabled(True)
            data.w_project.push_new.setDefault(False)

            self.table.setFocus()

        else:

            data.w_project.text_description.clear()
            data.w_project.text_description.setEnabled(False)
            data.c_main.dissableTabs()
            data.w_project.push_edit.setEnabled(False)
            data.w_project.push_delete.setEnabled(False)
            data.w_project.push_save.setEnabled(False)
            data.w_project.push_new.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onNewProject(self):

        timestamp = int(time.time())
        pid = data.project[0]['next_id']

        # create new project entry
        # meta: general project data
        # log: log data
        # milestone: versions, features, issues
        p = data.project[pid] = {
            'meta': {'last_log': 0, 'last_roadmap_item': 0,
                     'current_milestone': (0,0)},
            'log': {},
            'milestone' : [
                [{'description': '', 'm': '0.1',
                  'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}],
                [{'description': '', 'm': '1.0',
                  'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
                ],
            'ri_index' : {}
         }

        p['name']        = name        = self.diag_new.line_name.text()
        p['category']    = category    \
                = self.diag_new.combo_category.currentText()
        p['status']      = status      \
                = self.diag_new.combo_status.currentText()
        p['ptype']       = ptype       \
                = self.diag_new.combo_ptype.currentText()
        p['priority']    = priority    = self.diag_new.spin_priority.value()
        p['challenge']   = challenge   = self.diag_new.spin_challenge.value()
        p['description'] = description \
                = self.diag_new.text_description.toPlainText()
        p['created']     = created     = timestamp
        p['modified']    = timestamp

        data.project[0]['next_id'] += 1

        self.reloadTable()
        self.touchProject(timestamp)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def showEditProject(self):

        p = data.project[self.getPid()]

        self.diag_edit.line_name.setText(p['name'])
        self.diag_edit.combo_ptype.setCurrentIndex(
            self.diag_edit.combo_ptype.findText(p['ptype']))
        self.diag_edit.combo_status.setCurrentIndex(
            self.diag_edit.combo_status.findText(p['status']))
        self.diag_edit.combo_category.setCurrentIndex(
            self.diag_edit.combo_category.findText(p['category']))
        self.diag_edit.spin_priority.setValue(p['priority'])
        self.diag_edit.spin_challenge.setValue(p['challenge'])
        self.diag_edit.text_description.setPlainText(p['description'])

        self.diag_edit.show()
        self.diag_edit.line_name.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onEditProject(self):

        pid = self.getSelectedProject()
        p = data.project[pid]
        timestamp = int(time.time())
        disptime = datetime.datetime.fromtimestamp(timestamp).isoformat()

        p['name']        = self.diag_edit.line_name.text()
        p['category']    = self.diag_edit.combo_category.currentText()
        p['status']      = self.diag_edit.combo_status.currentText()
        p['ptype']       = self.diag_edit.combo_ptype.currentText()
        p['priority']    = self.diag_edit.spin_priority.value()
        p['challenge']   = self.diag_edit.spin_challenge.value()
        p['description'] = self.diag_edit.text_description.toPlainText()

        self.reloadTable()
        self.touchProject(timestamp)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDeleteProject(self):

        pid = self.getSelectedProject()

        response = QMessageBox.question(
            data.w_project,
            'Delete project?',
            'Sure you want to delete project {}: {}?'.format(
                str(pid), self.getSelectedProjectName()),
            QMessageBox.Yes|QMessageBox.No)

        if response == QMessageBox.StandardButton.No:
            return

        del data.project[pid]
        self.reloadTable()

        # can't touch deleted project, direct changed update
        data.run['changed'] = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reset(self):

        self.reloadTable()
        data.run['changed'] = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

