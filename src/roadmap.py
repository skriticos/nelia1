# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, time, gzip, pickle, datetime
from pprint import pprint
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton
from milestone import *
from datastore import data, convert
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxRoadmap:

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self):
        # used in saveLayout and loadLayout
        self.filter_names = ['feature', 'issue', 'open', 'closed', 'low',
                             'medium', 'high', 'core', 'auxiliary', 'security',
                             'corrective', 'architecture', 'refactor']
        # setup table
        self.feature_headers = \
            ['ID', 'Name', 'Type', 'Status', 'Category', 'Priority',
             'Created', 'Modified']

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        self.table = dc.ui.roadmap.v.table
        self.table.setModel(self.model)
        self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        self.table.setAlternatingRowColors(True)

        # connect feature / issue add push buttons
        dc.ui.roadmap.v.push_add_feature.clicked.connect(lambda: (
            dc.ui.roadmap_diag_add.v.radio_feature.setChecked(True),
            self.showAddEditMI('add')))
        dc.ui.roadmap.v.push_add_issue.clicked.connect(lambda: (
            dc.ui.roadmap_diag_add.v.radio_issue.setChecked(True),
            self.showAddEditMI('add')))
        dc.ui.roadmap_diag_add.v.accepted.connect(self.onSubmitDialog)

        # connect all the filter checkboxes to update the milestone item table
        dc.ui.roadmap.v.check_feature.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_issue.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_open.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_closed.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_low.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_medium.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_high.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_core.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_auxiliary.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_security.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_corrective.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_architecture.stateChanged.connect(self.reloadTable)
        dc.ui.roadmap.v.check_refactor.stateChanged.connect(self.reloadTable)

        # connect push milestone item action push buttons
        dc.ui.roadmap.v.push_delete.clicked.connect(self.deleteMilestoneItem)
        dc.ui.roadmap.v.push_edit.clicked.connect(lambda:(
            self.showAddEditMI('edit')))
        dc.ui.roadmap.v.push_close.clicked.connect(self.closeMilestoneItem)

        # connect finalize widget button callbacks
        dc.ui.roadmap_diag_finalize.v.push_finalize_major.clicked.connect(
            self.onCloseMajorMilestone)
        dc.ui.roadmap_diag_finalize.v.push_finalize_minor.clicked.connect(
            self.onCloseMinorMilestone)

        # connect selection changed (for close item)
        self.selection_model.selectionChanged.connect(
            self.onItemSelectionChanged
        )
        # connect milestone description changed
        dc.ui.roadmap.v.text_description.textChanged.connect(
            self.onMilestoneDescriptionChanged
        )

        # selection activate callback
        self.table.activated.connect(
            self.onMilestoneItemActivated
        )

        dc.ui.roadmap.v.label_selected.hide()
        dc.ui.roadmap.v.push_edit.hide()
        dc.ui.roadmap.v.push_delete.hide()
        dc.ui.roadmap.v.push_close.hide()

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
            w = dc.ui.roadmap.v
            target_label = w.push_target.text()
        elif targetw == 'add_edit_dialog':
            d = dc.ui.roadmap_diag_add.v
            target_label = d.push_target.text()

        tmajor, tminor = target_label.split(' ')[3][1:].split('.')
        return int(tmajor), int(tminor)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onItemSelectionChanged(self):

        if self.table.currentIndex().row() == -1: return
        status = self.model.itemFromIndex(self.model.index(
            self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            dc.ui.roadmap.v.push_close.setText('&Close Item')
        if status == 'Closed':
            dc.ui.roadmap.v.push_close.setText('Reopen Ite&m')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMilestoneDescriptionChanged(self):

        if self.init: return

        sx, sy = self.selected_major, \
                 minorIndex(self.selected_major, self.selected_minor)
        data.spro['milestone'][sx][sy]['description'] \
                = dc.ui.roadmap.v.text_description.toPlainText()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMilestoneItemActivated(self):

        cmajor, cminor \
                = data.spro['meta']['current_milestone']
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

            pro = data.spro

            dc.ui.roadmap.v.line_project.setText(data.spro['name'])
            dc.ui.roadmap_diag_add.v.line_project.setText(data.spro['name'])

            x, y = pro['meta']['current_milestone']
            milestones = pro['milestone']

            dc.ui.roadmap.v.gridLayout_3.removeWidget(dc.ui.roadmap.v.push_milestone)
            dc.ui.roadmap.v.push_milestone.close()
            dc.ui.roadmap.v.push_milestone = MPushButton(
                x, y, milestones, dc.ui.roadmap.v, self.onChangeVersionSelection)
            dc.ui.roadmap.v.gridLayout_3.addWidget(
                dc.ui.roadmap.v.push_milestone, 0, 1, 1, 1)
            dc.ui.roadmap.v.label_2.setBuddy(dc.ui.roadmap.v.push_milestone)

            self.reloadTable()

            # computing next_x, next_y is quite tricky, so we take it
            # from the milestone widget (which does it anyway)
            major = self.selected_major = dc.ui.roadmap.v.push_milestone.next_x
            minor = self.selected_minor = dc.ui.roadmap.v.push_milestone.next_y

            self.onChangeVersionSelection(major, minor)

            d = dc.ui.roadmap_diag_add.v
            d.radio_medium.setChecked(True)
            d.radio_feature.setChecked(True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMilestoneItem(self):

        status = self.model.itemFromIndex(self.model.index(
            self.table.currentIndex().row(),3)).text()
        if status == 'Open':
            # check if this is the last item in the milestone
            x, y = self.selected_major, \
                   minorIndex(self.selected_major, self.selected_minor)
            fo_sum = len(data.spro
                         ['milestone'] [x] [y] ['fo'])
            io_sum = len(data.spro
                         ['milestone'] [x] [y] ['io'])
            if fo_sum + io_sum == 1:
                self.closeMilestone(x, y)
            else:
                closeItem(self.getSelectedItemId())
        if status == 'Closed':
            reopenItem(self.getSelectedItemId())
        dc.m.project.v.touchProject()
        self.onChangeVersionSelection(self.selected_major, self.selected_minor)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMilestone(self, x, y):

        fo_sum1 = len(data.spro
                      ['milestone'] [x] [y+1] ['fo'])
        io_sum1 = len(data.spro
                      ['milestone'] [x] [y+1] ['io'])
        if fo_sum1 + io_sum1 == 0:
            dc.ui.roadmap_diag_finalize.v.push_finalize_major.setEnabled(
                True)
        else:
            dc.ui.roadmap_diag_finalize.v.push_finalize_major.setEnabled(
                False)

        dc.ui.roadmap_diag_finalize.v.show()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMinorMilestone(self):

        closeItem(self.getSelectedItemId())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMajorMilestone(self):

        closeItem(self.getSelectedItemId())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadMilestoneButton(self, targetw='root'):

        cmajor, cminor \
                = data.spro['meta']['current_milestone']
        milestones = data.spro['milestone']
        if targetw == 'root':
            dc.ui.roadmap.v.gridLayout_3.removeWidget(dc.ui.roadmap.v.push_milestone)
            dc.ui.roadmap.v.push_milestone.hide()
            dc.ui.roadmap.v.push_milestone.close()
            dc.ui.roadmap.v.push_milestone = MPushButton(
                cmajor, cminor, milestones, dc.ui.roadmap.v,
                self.onChangeVersionSelection,
                self.selected_major, self.selected_minor)
            dc.ui.roadmap.v.gridLayout_3.addWidget(
                dc.ui.roadmap.v.push_milestone, 0, 1, 1, 1)
            dc.ui.roadmap.v.label_2.setBuddy(dc.ui.roadmap.v.push_milestone)
        elif targetw == 'diag_new_edit':
            dc.ui.roadmap_diag_add.v.gridLayout_2.removeWidget(
                dc.ui.roadmap_diag_add.v.push_target)
            dc.ui.roadmap_diag_add.v.push_target.close()
            dc.ui.roadmap_diag_add.v.push_target \
                    = MPushButton(cmajor,cminor,milestones,
                                  dc.ui.roadmap_diag_add.v,None,self.selected_major,
                                  self.selected_minor,True)
            dc.ui.roadmap_diag_add.v.gridLayout_2.addWidget(
                dc.ui.roadmap_diag_add.v.push_target, 1, 1, 1, 1);
            dc.ui.roadmap_diag_add.v.label_3.setBuddy(dc.ui.roadmap_diag_add.v.push_target)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onChangeVersionSelection(self, major, minor, text=None):

        self.selected_major = major
        self.selected_minor = minor
        sx, sy = major, minorIndex(major, minor)
        dc.ui.roadmap.v.text_description.setPlainText(
            data.spro['milestone'][sx][sy]['description']
        )
        self.reloadMilestoneButton('root')
        self.reloadTable()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def prependTable(self, key, itype, status, priority, icat, v):

        if itype == 'Feature' \
           and not dc.ui.roadmap.v.check_feature.isChecked(): return
        if itype == 'Issue' \
           and not dc.ui.roadmap.v.check_issue.isChecked(): return
        if status == 'Open' \
           and not dc.ui.roadmap.v.check_open.isChecked(): return
        if status == 'Closed' \
           and not dc.ui.roadmap.v.check_closed.isChecked(): return
        if priority == 'Low' \
           and not dc.ui.roadmap.v.check_low.isChecked(): return
        if priority == 'Medium' \
           and not dc.ui.roadmap.v.check_medium.isChecked(): return
        if priority == 'High' \
           and not dc.ui.roadmap.v.check_high.isChecked(): return
        if icat == 'Core' \
           and not dc.ui.roadmap.v.check_core.isChecked(): return
        if icat == 'Auxiliary' \
           and not dc.ui.roadmap.v.check_auxiliary.isChecked(): return
        if icat == 'Security' \
           and not dc.ui.roadmap.v.check_security.isChecked(): return
        if icat == 'Corrective' \
           and not dc.ui.roadmap.v.check_corrective.isChecked(): return
        if icat == 'Architecture' \
           and not dc.ui.roadmap.v.check_architecture.isChecked(): return
        if icat == 'Refactor' \
           and not dc.ui.roadmap.v.check_refactor.isChecked(): return

        self.model.insertRow(0, [
            QStandardItem(str(key).zfill(4)),
            QStandardItem(v['name']),
            QStandardItem(itype),
            QStandardItem(status),
            QStandardItem(icat),
            QStandardItem(str(v['priority'])),
            QStandardItem(convert(v['created'])),
            QStandardItem(convert(v['modified']))
        ])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        dc.c.roadmap.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.roadmap.header.width.v.append(self.table.columnWidth(i))
        dc.c.roadmap.sort.column.v \
                = self.horizontal_header.sortIndicatorSection()
        dc.c.roadmap.sort.order.v \
                = self.horizontal_header.sortIndicatorOrder().__repr__()
        # save filter checkbox states
        for filter_name in self.filter_names:
            dc.c.roadmap._('show_{}'.format(filter_name)).v \
                    = dc.ui.roadmap.v.__dict__['check_{}'.format(filter_name)] \
                    .isChecked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for i,v in enumerate(dc.c.roadmap.header.width.v):
            self.table.setColumnWidth(i, v)
        if dc.c.roadmap.sort.column.v:
            self.horizontal_header.setSortIndicator(
                dc.c.roadmap.sort.column.v,
                convert(dc.c.roadmap.sort.order.v))
        # restore filter checkbox states
        for filter_name in self.filter_names:
            dc.ui.roadmap.v.__dict__['check_{}'.format(filter_name)].setChecked(
                    dc.c.roadmap._('show_{}'.format(filter_name)).v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self, state=None, preserveLayout=True):

        if not isinstance(dc.ui.roadmap.v.push_milestone, MPushButton):
            return

        self.init = True

        if preserveLayout:
            self.saveLayout()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(self.feature_headers)
        dc.ui.roadmap.v.push_close.setText('&Close Item')

        self.selected_major, self.selected_minor \
                = dc.ui.roadmap.v.push_milestone.getVersion()
        cmajor, cminor = data.spro['meta']['current_milestone']
        yy = self.selected_minor
        if self.selected_major == 0: yy = self.selected_minor-1
        fo = data.spro['milestone'][self.selected_major][yy]['fo']
        fc = data.spro['milestone'][self.selected_major][yy]['fc']
        io = data.spro['milestone'][self.selected_major][yy]['io']
        ic = data.spro['milestone'][self.selected_major][yy]['ic']

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
                dc.ui.roadmap.v.label_selected.show()
                dc.ui.roadmap.v.push_edit.show()
                dc.ui.roadmap.v.push_delete.show()
                dc.ui.roadmap.v.push_close.show()
            else:
                dc.ui.roadmap.v.label_selected.hide()
                dc.ui.roadmap.v.push_edit.hide()
                dc.ui.roadmap.v.push_delete.hide()
                dc.ui.roadmap.v.push_close.hide()
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
            dc.ui.roadmap_diag_add.v.setWindowTitle('Add Roadmap Item')
            dc.ui.roadmap_diag_add.v.line_name.clear()
            dc.ui.roadmap_diag_add.v.text_description.clear()
        else:
            self.diag_type = 'edit'
            dc.ui.roadmap_diag_add.v.setWindowTitle('Edit Roadmap Item')

            item_id = self.getSelectedItemId()
            tmajor, tminor, fioc \
                    = data.spro['mi_index'][item_id]
            tx, ty = tmajor, minorIndex(tmajor, tminor)
            item = data.spro\
                    ['milestone'][tx][ty][fioc][item_id]

            if fioc[0] == 'f': itype = 'Feature'
            if fioc[0] == 'i': itype = 'Isssue'

            if itype == 'Feature':
                dc.ui.roadmap_diag_add.v.radio_feature.setChecked(True)
            if itype == 'Issue':
                dc.ui.roadmap_diag_add.v.radio_issue.setChecked(True)
            if item['priority'] == 'Low':
                dc.ui.roadmap_diag_add.v.radio_low.setChecked(True)
            if item['priority'] == 'Medium':
                dc.ui.roadmap_diag_add.v.radio_medium.setChecked(True)
            if item['priority'] == 'High':
                dc.ui.roadmap_diag_add.v.radio_high.setChecked(True)
            if item['icat'] == 'Core':
                dc.ui.roadmap_diag_add.v.radio_core.setChecked(True)
            if item['icat'] == 'Auxiliary':
                dc.ui.roadmap_diag_add.v.radio_auxiliary.setChecked(True)
            if item['icat'] == 'Security':
                dc.ui.roadmap_diag_add.v.radio_security.setChecked(True)
            if item['icat'] == 'Corrective':
                dc.ui.roadmap_diag_add.v.radio_corrective.setChecked(True)
            if item['icat'] == 'Architecture':
                dc.ui.roadmap_diag_add.v.radio_architecture.setChecked(True)
            if item['icat'] == 'Refactor':
                dc.ui.roadmap_diag_add.v.radio_refactor.setChecked(True)

            dc.ui.roadmap_diag_add.v.line_name.setText(item['name'])
            dc.ui.roadmap_diag_add.v.text_description.setPlainText(
                item['description'])

        # show dialog
        dc.ui.roadmap_diag_add.v.show()
        dc.ui.roadmap_diag_add.v.line_name.setFocus()

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

        name = dc.ui.roadmap_diag_add.v.line_name.text()
        description = dc.ui.roadmap_diag_add.v.text_description.toPlainText()

        if dc.ui.roadmap_diag_add.v.radio_feature.isChecked():
            ri_type = 'Feature'
        else:
            ri_type = 'Issue'

        if dc.ui.roadmap_diag_add.v.radio_medium.isChecked():
            priority = 'Medium'
        elif dc.ui.roadmap_diag_add.v.radio_high.isChecked():
            priority = 'High'
        elif dc.ui.roadmap_diag_add.v.radio_low.isChecked():
            priority = 'Low'

        if dc.ui.roadmap_diag_add.v.radio_core.isChecked():
            category = 'Core'
        elif dc.ui.roadmap_diag_add.v.radio_auxiliary.isChecked():
            category = 'Auxiliary'
        elif dc.ui.roadmap_diag_add.v.radio_security.isChecked():
            category = 'Security'
        elif dc.ui.roadmap_diag_add.v.radio_corrective.isChecked():
            category = 'Corrective'
        elif dc.ui.roadmap_diag_add.v.radio_architecture.isChecked():
            category = 'Architecture'
        elif dc.ui.roadmap_diag_add.v.radio_refactor.isChecked():
            category = 'Refactor'

        if mode == 'add':
            addItem(tmajor, tminor, ri_type, category,
                    name, priority, description)
        if mode == 'edit':
            editItem(tmajor, tminor, self.getSelectedItemId(),
                     ri_type, category, name, priority, description)

        self.reloadMilestoneButton()
        self.reloadTable()

        dc.m.project.v.touchProject()
        print('touching project')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteMilestoneItem(self):

        deleteItem(self.getSelectedItemId())
        self.reloadMilestoneButton()
        self.reloadTable()
        dc.m.project.v.touchProject()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

