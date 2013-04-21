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
        if 'lastpath' not in data.conf['datastore']:
            data.w_project.push_open_last.hide()

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
            self.onDescriptionChanged)

        self.table.activated.connect(self.showEditProject)

        # global handles for getting currently selected pid and updating
        # timestamp for currently selected project
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
        data.w_project.push_save.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onOpenLast(self):
        path = data.conf['datastore']['lastpath']
        result = data.open_document(path)
        if isinstance(result, Exception):
            title, message = 'Open failed', 'Open failed! ' + str(result)
            QMessageBox.critical(data.w_main, title, message)
            return
        self.reset()
        data.w_project.push_open_last.hide()
        data.w_project.push_save.hide()
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
        data.w_project.push_save.hide()
        self.table.setFocus()
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
        row = self.table.currentIndex().row()
        self.model.setItem(row, 8,
            QStandardItem(datetime.datetime.fromtimestamp(timestamp).isoformat()))
        data.run['changed'] = True
        data.w_project.push_save.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSelectionChanged(self):
        # set selected project id and store dictionary reference
        row = self.table.currentIndex().row()
        if row == -1: return
        index = self.model.index(row, 0)
        data.spid = int(self.model.itemFromIndex(index).text())
        data.spro = data.project[data.spid]
        # update content and enable project description widget
        for w in [data.w_project.text_description]:
            w.setPlainText(data.spro['description'])
            w.setEnabled(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDescriptionChanged(self):
        if self.init: return
        data.spro['description'] = \
                data.w_project.text_description.toPlainText()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        data.conf['project']['header_width'] = list()
        for i in range(10):
            data.conf['project']['header_width'].append(
                self.table.columnWidth(i))
        data.conf['project']['sort_column'] \
                = self.horizontal_header.sortIndicatorSection()
        data.conf['project']['sort_order'] \
                = self.horizontal_header.sortIndicatorOrder().__repr__()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(data.conf['project']['header_width']):
            self.table.setColumnWidth(i, v)
        if data.conf['project']['sort_column']:
            self.horizontal_header.setSortIndicator(
                data.conf['project']['sort_column'],
                data.convert(data.conf['project']['sort_order']))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self, state=None, preserveLayout=True):

        self.init = True

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.table_headers)

        if len(data.project) > 1:
            data.w_project.push_open_last.hide()

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


        if len(data.project) > 1:

            self.table.selectRow(0)

            data.c_main.enableTabs()
            data.w_project.push_edit.show()
            data.w_project.push_delete.show()
            data.w_project.push_save.show()
            data.w_project.push_new.setDefault(False)

            self.table.setFocus()

        else:

            data.w_project.text_description.clear()
            data.w_project.text_description.setEnabled(False)
            data.c_main.dissableTabs()
            data.w_project.push_edit.hide()
            data.w_project.push_delete.hide()
            data.w_project.push_save.hide()
            data.w_project.push_new.setFocus()

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
            'mi_index' : {}
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

        data.project[0]['next_pid'] += 1

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
            data.w_project,
            'Delete project?',
            'Sure you want to delete project {}: {}?'.format(
                str(data.spid), data.spro['name']),
            QMessageBox.Yes|QMessageBox.No)

        if response == QMessageBox.StandardButton.No:
            return

        del data.spro
        self.reloadTable()

        # can't touch deleted project, direct changed update
        data.run['changed'] = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reset(self):

        self.reloadTable()
        data.run['changed'] = False

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

