# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, time, gzip, pickle, datetime
from pprint import pprint
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton
from milestone import NxMilestone
from datastore import data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxRoadmap:

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        # used in saveLayout and loadLayout
        self.filter_names = ['feature', 'issue', 'open', 'closed', 'low',
                             'medium', 'high', 'core', 'auxiliary', 'security',
                             'corrective', 'architecture', 'refactor']
        # setup backbone
        self.mc     = NxMilestone()

        # setup table
        self.feature_headers = \
            ['ID', 'Name', 'Type', 'Status', 'Category', 'Priority',
             'Created', 'Modified']

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        self.table = data.w_roadmap.table
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        self.table.setAlternatingRowColors(True)

        # connect feature / issue add push buttons
        data.w_roadmap.push_add_feature.clicked.connect(lambda: (
            data.w_roadmap_diag_add.radio_feature.setChecked(True),
            self.showAddEditMI('add')))
        data.w_roadmap.push_add_issue.clicked.connect(lambda: (
            data.w_roadmap_diag_add.radio_issue.setChecked(True),
            self.showAddEditMI('add')))
        data.w_roadmap_diag_add.accepted.connect(self.onSubmitDialog)

        # connect all the filter checkboxes to update the milestone item table
        data.w_roadmap.check_feature.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_issue.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_open.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_closed.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_low.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_medium.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_high.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_core.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_auxiliary.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_security.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_corrective.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_architecture.stateChanged.connect(self.reloadTable)
        data.w_roadmap.check_refactor.stateChanged.connect(self.reloadTable)

        # connect push milestone item action push buttons
        data.w_roadmap.push_delete.clicked.connect(self.deleteMilestoneItem)
        data.w_roadmap.push_edit.clicked.connect(lambda:(
            self.showAddEditMI('edit')))
        data.w_roadmap.push_close.clicked.connect(self.closeMilestoneItem)

        # connect finalize widget button callbacks
        data.w_roadmap_diag_finalize.push_finalize_major.clicked.connect(
            self.onCloseMajorMilestone)
        data.w_roadmap_diag_finalize.push_finalize_minor.clicked.connect(
            self.onCloseMinorMilestone)

        # connect selection changed (for close item)
        self.selection_model.selectionChanged.connect(
            self.onItemSelectionChanged
        )
        # connect milestone description changed
        data.w_roadmap.text_description.textChanged.connect(
            self.onMilestoneDescriptionChanged
        )

        # selection activate callback
        self.table.activated.connect(
            self.onMilestoneItemActivated
        )

        data.w_roadmap.label_selected.hide()
        data.w_roadmap.push_edit.hide()
        data.w_roadmap.push_delete.hide()
        data.w_roadmap.push_close.hide()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getCellContent(self, i):

        return int(self.model.itemFromIndex(
            self.model.index(
                self.table.currentIndex().row(),i)
        ).text())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getSelectedItemId(self):

        return self.getCellContent(0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def extractSelection(self, targetw='root'):

        if targetw == 'root':
            w = data.w_roadmap
            target_label = w.push_target.text()
        elif targetw == 'add_edit_dialog':
            d = data.w_roadmap_diag_add
            target_label = d.push_target.text()

        tmajor, tminor = target_label.split(' ')[3][1:].split('.')
        return int(tmajor), int(tminor)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onItemSelectionChanged(self):

        if self.table.currentIndex().row() == -1: return
        status = self.model.itemFromIndex(self.model.index(
            self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            data.w_roadmap.push_close.setText('&Close Item')
        if status == 'Closed':
            data.w_roadmap.push_close.setText('Reopen Ite&m')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMilestoneDescriptionChanged(self):

        if self.init: return

        sx, sy = self.mc.versionToIndex(
            self.selected_major, self.selected_minor)
        data.project[data.spid]['milestone'][sx][sy]['description'] \
                = data.w_roadmap.text_description.toPlainText()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMilestoneItemActivated(self):

        cmajor, cminor \
                = data.project[data.spid]['meta']['current_milestone']
        if self.model.rowCount() > 0:
            if self.selected_major > cmajor \
               or (self.selected_major == cmajor \
                   and self.selected_minor > cminor):
                self.showAddEditMI('edit')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowTab(self):

        if data.run['roadmap_pid_last'] == 0 \
           or data.run['roadmap_pid_last'] != data.spid:

            data.run['roadmap_pid_last'] = data.spid

            pro = data.project[data.spid]

            project_name = data.c_project.getSelectedProjectName()
            data.w_roadmap.line_project.setText(project_name)
            data.w_roadmap_diag_add.line_project.setText(project_name)

            x, y = pro['meta']['current_milestone']
            milestones = pro['milestone']

            data.w_roadmap.gridLayout_3.removeWidget(data.w_roadmap.push_milestone)
            data.w_roadmap.push_milestone.close()
            data.w_roadmap.push_milestone = MPushButton(
                x, y, milestones, data.w_roadmap, self.onChangeVersionSelection)
            data.w_roadmap.gridLayout_3.addWidget(
                data.w_roadmap.push_milestone, 0, 1, 1, 1)
            data.w_roadmap.label_2.setBuddy(data.w_roadmap.push_milestone)

            self.reloadTable()

            # computing next_x, next_y is quite tricky, so we take it
            # from the milestone widget (which does it anyway)
            major = self.selected_major = data.w_roadmap.push_milestone.next_x
            minor = self.selected_minor = data.w_roadmap.push_milestone.next_y

            self.onChangeVersionSelection(major, minor)

            d = data.w_roadmap_diag_add
            d.radio_medium.setChecked(True)
            d.radio_feature.setChecked(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMilestoneItem(self):

        status = self.model.itemFromIndex(self.model.index(
            self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            # check if this is the last item in the milestone
            x, y = self.mc.versionToIndex(
                self.selected_major, self.selected_minor)
            fo_sum = len(data.project[data.spid]
                         ['milestone'] [x] [y] ['fo'])
            io_sum = len(data.project[data.spid]
                         ['milestone'] [x] [y] ['io'])
            if fo_sum + io_sum == 1:
                self.closeMilestone(x, y)
            else:
                self.mc.closeItem(data.spid, self.getSelectedItemId())
        if status == 'Closed':
            self.mc.reopenItem(data.spid, self.getSelectedItemId())
        data.touchProject()
        self.onChangeVersionSelection(self.selected_major, self.selected_minor)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMilestone(self, x, y):

        fo_sum1 = len(data.project[data.spid]
                      ['milestone'] [x] [y+1] ['fo'])
        io_sum1 = len(data.project[data.spid]
                      ['milestone'] [x] [y+1] ['io'])
        if fo_sum1 + io_sum1 == 0:
            data.w_roadmap_diag_finalize.push_finalize_major.setEnabled(
                True)
        else:
            data.w_roadmap_diag_finalize.push_finalize_major.setEnabled(
                False)

        data.w_roadmap_diag_finalize.show()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMinorMilestone(self):

        self.mc.closeItem(data.spid, self.getSelectedItemId())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMajorMilestone(self):

        self.mc.closeItem(data.spid, self.getSelectedItemId())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadMilestoneButton(self, targetw='root'):

        cmajor, cminor \
                = data.project[data.spid]['meta']['current_milestone']
        milestones = data.project[data.spid]['milestone']
        if targetw == 'root':
            data.w_roadmap.gridLayout_3.removeWidget(data.w_roadmap.push_milestone)
            data.w_roadmap.push_milestone.hide()
            data.w_roadmap.push_milestone.close()
            data.w_roadmap.push_milestone = MPushButton(
                cmajor, cminor, milestones, data.w_roadmap,
                self.onChangeVersionSelection,
                self.selected_major, self.selected_minor)
            data.w_roadmap.gridLayout_3.addWidget(
                data.w_roadmap.push_milestone, 0, 1, 1, 1)
            data.w_roadmap.label_2.setBuddy(data.w_roadmap.push_milestone)
        elif targetw == 'diag_new_edit':
            data.w_roadmap_diag_add.gridLayout_2.removeWidget(
                data.w_roadmap_diag_add.push_target)
            data.w_roadmap_diag_add.push_target.close()
            data.w_roadmap_diag_add.push_target \
                    = MPushButton(cmajor,cminor,milestones,
                                  data.w_roadmap_diag_add,None,self.selected_major,
                                  self.selected_minor,True)
            data.w_roadmap_diag_add.gridLayout_2.addWidget(
                data.w_roadmap_diag_add.push_target, 1, 1, 1, 1);
            data.w_roadmap_diag_add.label_3.setBuddy(data.w_roadmap_diag_add.push_target)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onChangeVersionSelection(self, major, minor, text=None):

        self.selected_major = major
        self.selected_minor = minor
        sx, sy = self.mc.versionToIndex(major, minor)
        data.w_roadmap.text_description.setPlainText(
            data.project[data.spid]['milestone'][sx][sy]['description']
        )
        self.reloadMilestoneButton('root')
        self.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def prependTable(self, key, itype, status, priority, icat, v):

        if itype == 'Feature' \
           and not data.w_roadmap.check_feature.isChecked(): return
        if itype == 'Issue' \
           and not data.w_roadmap.check_issue.isChecked(): return
        if status == 'Open' \
           and not data.w_roadmap.check_open.isChecked(): return
        if status == 'Closed' \
           and not data.w_roadmap.check_closed.isChecked(): return
        if priority == 'Low' \
           and not data.w_roadmap.check_low.isChecked(): return
        if priority == 'Medium' \
           and not data.w_roadmap.check_medium.isChecked(): return
        if priority == 'High' \
           and not data.w_roadmap.check_high.isChecked(): return
        if icat == 'Core' \
           and not data.w_roadmap.check_core.isChecked(): return
        if icat == 'Auxiliary' \
           and not data.w_roadmap.check_auxiliary.isChecked(): return
        if icat == 'Security' \
           and not data.w_roadmap.check_security.isChecked(): return
        if icat == 'Corrective' \
           and not data.w_roadmap.check_corrective.isChecked(): return
        if icat == 'Architecture' \
           and not data.w_roadmap.check_architecture.isChecked(): return
        if icat == 'Refactor' \
           and not data.w_roadmap.check_refactor.isChecked(): return

        self.model.insertRow(0, [
            QStandardItem(str(key).zfill(4)),
            QStandardItem(v['name']),
            QStandardItem(itype),
            QStandardItem(status),
            QStandardItem(icat),
            QStandardItem(str(v['priority'])),
            QStandardItem(datetime.datetime.fromtimestamp(
                v['created']).isoformat()),
            QStandardItem(datetime.datetime.fromtimestamp(
                v['modified']).isoformat())
        ])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        data.conf['roadmap']['header_width'] = []
        for i in range(8):
            data.conf['roadmap']['header_width'].append(
                self.table.columnWidth(i))
        if self.horizontal_header.sortIndicatorSection() < 8:
            data.conf['roadmap']['sort_column'] \
                    = self.horizontal_header.sortIndicatorSection()
            data.conf['roadmap']['sort_order'] \
                    = self.horizontal_header.sortIndicatorOrder().__repr__()
        else:
            data.conf['roadmap']['sort_column'] = -1
            data.conf['roadmap']['sort_order'] = None
        # save filter checkbox states
        for filter_name in self.filter_names:
            data.conf['roadmap']['show_{}'.format(filter_name)] \
                    = data.w_roadmap.__dict__['check_{}'.format(filter_name)] \
                    .isChecked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(data.conf['roadmap']['header_width']):
            self.table.setColumnWidth(i, v)
        if data.conf['roadmap']['sort_column'] != -1:
            self.horizontal_header.setSortIndicator(
                data.conf['roadmap']['sort_column'],
                data.convert(data.conf['roadmap']['sort_order']))
        # restore filter checkbox states
        for filter_name in self.filter_names:
            data.w_roadmap.__dict__['check_{}'.format(filter_name)].setChecked(
                    data.conf['roadmap']['show_{}'.format(filter_name)])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self, state=None, preserveLayout=True):

        if not isinstance(data.w_roadmap.push_milestone, MPushButton):
            return

        self.init = True

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        data.w_roadmap.push_close.setText('&Close Item')

        self.selected_major, self.selected_minor \
                = data.w_roadmap.push_milestone.getVersion()
        cmajor, cminor = data.project[data.spid]['meta']['current_milestone']
        yy = self.selected_minor
        if self.selected_major == 0: yy = self.selected_minor-1
        fo = data.project[data.spid]['milestone'][self.selected_major][yy]['fo']
        fc = data.project[data.spid]['milestone'][self.selected_major][yy]['fc']
        io = data.project[data.spid]['milestone'][self.selected_major][yy]['io']
        ic = data.project[data.spid]['milestone'][self.selected_major][yy]['ic']

        for key, value in ic.items():
            itype = 'Issue'
            status = 'Closed'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in fc.items():
            itype = 'Feature'
            status = 'Closed'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in io.items():
            itype = 'Issue'
            status = 'Open'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)
        for key, value in fo.items():
            itype = 'Feature'
            status = 'Open'
            icat = value['icat']
            priority = value['priority']
            self.prependTable(key, itype, status, priority, icat, value)

        self.init = False

        # only enable controls for future milestones
        if self.model.rowCount() > 0:
            if self.selected_major > cmajor \
               or (self.selected_major == cmajor \
                   and self.selected_minor > cminor):
                data.w_roadmap.label_selected.show()
                data.w_roadmap.push_edit.show()
                data.w_roadmap.push_delete.show()
                data.w_roadmap.push_close.show()
            else:
                data.w_roadmap.label_selected.hide()
                data.w_roadmap.push_edit.hide()
                data.w_roadmap.push_delete.hide()
                data.w_roadmap.push_close.hide()
            self.table.selectRow(0)

        if preserveLayout:
            self.loadLayout()

        self.table.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def showAddEditMI(self, diag_type=None):

        self.reloadMilestoneButton('diag_new_edit')

        # set dialog type flag
        if diag_type == 'add':
            self.diag_type = 'add'
            data.w_roadmap_diag_add.setWindowTitle('Add Roadmap Item')
            data.w_roadmap_diag_add.line_name.clear()
            data.w_roadmap_diag_add.text_description.clear()
        else:
            self.diag_type = 'edit'
            data.w_roadmap_diag_add.setWindowTitle('Edit Roadmap Item')

            item_id = self.getSelectedItemId()
            tmajor, tminor, fioc \
                    = data.project[data.spid]['mi_index'][item_id]
            tx, ty = self.mc.versionToIndex(tmajor, tminor)
            item = data.project[data.spid]\
                    ['milestone'][tx][ty][fioc][item_id]

            if fioc[0] == 'f': itype = 'Feature'
            if fioc[0] == 'i': itype = 'Isssue'

            if itype == 'Feature':
                data.w_roadmap_diag_add.radio_feature.setChecked(True)
            if itype == 'Issue':
                data.w_roadmap_diag_add.radio_issue.setChecked(True)
            if item['priority'] == 'Low':
                data.w_roadmap_diag_add.radio_low.setChecked(True)
            if item['priority'] == 'Medium':
                data.w_roadmap_diag_add.radio_medium.setChecked(True)
            if item['priority'] == 'High':
                data.w_roadmap_diag_add.radio_high.setChecked(True)
            if item['icat'] == 'Core':
                data.w_roadmap_diag_add.radio_core.setChecked(True)
            if item['icat'] == 'Auxiliary':
                data.w_roadmap_diag_add.radio_auxiliary.setChecked(True)
            if item['icat'] == 'Security':
                data.w_roadmap_diag_add.radio_security.setChecked(True)
            if item['icat'] == 'Corrective':
                data.w_roadmap_diag_add.radio_corrective.setChecked(True)
            if item['icat'] == 'Architecture':
                data.w_roadmap_diag_add.radio_architecture.setChecked(True)
            if item['icat'] == 'Refactor':
                data.w_roadmap_diag_add.radio_refactor.setChecked(True)

            data.w_roadmap_diag_add.line_name.setText(item['name'])
            data.w_roadmap_diag_add.text_description.setPlainText(
                item['description'])

        # show dialog
        data.w_roadmap_diag_add.show()
        data.w_roadmap_diag_add.line_name.setFocus()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSubmitDialog(self):

        # simple switch between add and edit mode for the dialog
        if self.diag_type == 'add':
            self.onSubmitNewEditMI('add')
        if self.diag_type == 'edit':
            self.onSubmitNewEditMI('edit')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSubmitNewEditMI(self, mode):

        tmajor, tminor = self.extractSelection('add_edit_dialog')

        name = data.w_roadmap_diag_add.line_name.text()
        description = data.w_roadmap_diag_add.text_description.toPlainText()

        if data.w_roadmap_diag_add.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'

        if data.w_roadmap_diag_add.radio_medium.isChecked():
            priority = 'Medium'
        elif data.w_roadmap_diag_add.radio_high.isChecked():
            priority = 'High'
        elif data.w_roadmap_diag_add.radio_low.isChecked():
            priority = 'Low'

        if data.w_roadmap_diag_add.radio_core.isChecked():
            category = 'Core'
        elif data.w_roadmap_diag_add.radio_auxiliary.isChecked():
            category = 'Auxiliary'
        elif data.w_roadmap_diag_add.radio_security.isChecked():
            category = 'Security'
        elif data.w_roadmap_diag_add.radio_corrective.isChecked():
            category = 'Corrective'
        elif data.w_roadmap_diag_add.radio_architecture.isChecked():
            category = 'Architecture'
        elif data.w_roadmap_diag_add.radio_refactor.isChecked():
            category = 'Refactor'

        if mode == 'add':
            self.mc.addItem(
                data.spid, tmajor, tminor, ri_type, category,
                name, priority, description
            )
        if mode == 'edit':
            self.mc.editItem(
                data.spid, tmajor, tminor, self.getSelectedItemId(),
                ri_type, category, name, priority, description
            )

        self.reloadMilestoneButton()
        self.reloadTable()

        data.touchProject()
        print('touching project')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteMilestoneItem(self):

        self.mc.deleteItem(data.spid, self.getSelectedItemId())
        self.reloadMilestoneButton()
        self.reloadTable()
        data.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

