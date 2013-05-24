# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, time, gzip, pickle, datetime
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
from mpushbutton import MPushButton
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
filters = [
    'feature', 'issue', 'open', 'closed', 'low', 'medium', 'high',
   'core', 'auxiliary', 'security', 'corrective', 'architecture', 'refactor']
headers = [
    'ID', 'Name', 'Type', 'Status', 'Category', 'Priority',
    'Created', 'Modified']
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxRoadmap:
    def __init__(self):
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.table = dc.ui.roadmap.v.table
        self.table.setModel(self.model)
        selmod = self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        # setup callbacks
        win = dc.ui.roadmap.v
        win.push_add_feature.clicked.connect(self.onAddFeatureClicked)
        win.push_add_issue.clicked.connect(self.onAddIssueClicked)
        dc.ui.roadmap_diag_add.v.accepted.connect(self.onSubmitDialog)
        for f in filters:
            widget = win.__dict__['check_{}'.format(f)]
            widget.stateChanged.connect(self.reloadTable)
        win.push_delete.clicked.connect(self.onDeleteMIClicked)
        # TODO: separate add/edit dialogs
        win.push_edit.clicked.connect(self.onEditMIClicked)
        win.push_close.clicked.connect(self.onCloseMIClicked)
        dfin = dc.ui.roadmap_diag_finalize.v
        dfin.push_finalize_major.clicked.connect(self.onCloseMajorMilestone)
        dfin.push_finalize_minor.clicked.connect(self.onCloseMinorMilestone)
        selmod.selectionChanged.connect(self.onItemSelectionChanged)
        win.text_description.textChanged.connect(self.onMsDescChanged)
        self.table.activated.connect(self.onMilestoneItemActivated)
        for w in ['label_selected', 'push_edit', 'push_delete', 'push_close']:
            win.__dict__[w].hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAddFeatureClicked(self):
        dc.ui.roadmap_diag_add.v.radio_feature.setChecked(True)
        self.showAddEditMI('add')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAddIssueClicked(self):
        dc.ui.roadmap_diag_add.v.radio_issue.setChecked(True)
        self.showAddEditMI('add')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onEditMIClicked(self):
        self.showAddEditMI('edit')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateMilestoneTree(self):
        for imajor in reversed(list(dc.sp.m.idx.v)):
            # major branch receaves first item
            if imajor > 0 and imajor+1 not in dc.sp.m.idx.v \
                          and len(dc.sp.m._(imajor)._(0).idx.v):
                # add imajor+1.0, imajor.1
                dc.sp.m.idx.v.add(imajor+1)
                dc.sp.m._(imajor+1).idx.v = {0}
                dc.sp.m._(imajor+1)._(0).description.v = ''
                dc.sp.m._(imajor+1)._(0).idx.v = set()
                dc.sp.m._(imajor).idx.v.add(1)
                dc.sp.m._(imajor)._(1).description.v = ''
                dc.sp.m._(imajor)._(1).idx.v = set()
                continue
            # major branch looses last item
            elif imajor > 1 and not len(dc.sp.m._(imajor-1)._(0).idx.v):
                del dc.sp.m.__dict__['_{}'.format(imajor)]
                dc.sp.m.idx.v.remove(imajor)
                continue
            lminor = max(dc.sp.m._(imajor).idx.v)
            if imajor is 0 and lminor is 1 and not dc.sp.m._(0)._(1).idx.v:
                break
            # last minor branch receaves first item
            if len(dc.sp.m._(imajor)._(lminor).idx.v):
                dc.sp.m._(imajor).idx.v.add(lminor+1)
                dc.sp.m._(imajor)._(lminor+1).description.v = ''
                dc.sp.m._(imajor)._(lminor+1).idx.v = set()
            # previous to last minor branch looses last item
            elif lminor and not len(dc.sp.m._(imajor)._(lminor-1).idx.v):
                dc.sp.m._(imajor).idx.v.remove(lminor)
                del dc.sp.m._(imajor).__dict__['_{}'.format(lminor)]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addMI(self, major, minor, itype, category,
              name, priority, description, status='Open'):
        # milestone item id
        miid = dc.sp.nextmiid.v
        dc.sp.nextmiid.v += 1
        # milestone item location
        dc.sp.midx.v[miid] = major, minor
        # milestone item attributes
        dc.sp.mi._(miid).name.v = name
        dc.sp.mi._(miid).description.v = description
        dc.sp.mi._(miid).priority.v = priority
        dc.sp.mi._(miid).category.v = category
        dc.sp.mi._(miid).itype.v = itype
        dc.sp.mi._(miid).status.v = status
        t = int(time.time())
        dc.sp.mi._(miid).created.v = t
        dc.sp.mi._(miid).modified.v = t
        # milestone item reference in tree
        dc.sp.m._(major)._(minor).idx.v.add(miid)
        self.updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def editMI(self, major, minor, miid, itype, category, name,
               priority, description):
        if (major, minor) != dc.sp.midx.v[miid]:
            old_major, old_minor = dc.sp.midx.v[miid]
            dc.sp.m._(old_major)._(old_minor).idx.v.remove(miid)
            dc.sp.m._(major)._(minor).idx.v.add(miid)
            dc.sp.midx.v[miid] = major, minor
        dc.sp.mi._(miid).itype.v = itype
        dc.sp.mi._(miid).name.v  = name
        dc.sp.mi._(miid).category.v = category
        dc.sp.mi._(miid).priority.v = priority
        dc.sp.mi._(miid).description.v = description
        dc.sp.mi._(miid).changed.v = int(time.time())
        self.updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMI(self, miid):
        dc.sp.mi._(miid).status.v = 'Closed'
        dc.sp.mi._(miid).changed.v = int(time.time())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reopenMI(self, miid):
        dc.sp.mi._(miid).status.v = 'Open'
        dc.sp.mi._(miid).changed.v = int(time.time())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteMI(self, miid):
        del dc.sp.mi.__dict__['_{}'.format(miid)]
        major, minor = dc.sp.midx.v[miid]
        del dc.sp.midx.v[miid]
        dc.sp.m._(major)._(minor).idx.v.remove(miid)
        self.updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getCellContent(self, i):
        return int(self.model.itemFromIndex(
            self.model.index(self.table.currentIndex().row(),i)).text())
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
    def onMsDescChanged(self):
        if self.init: return
        description = dc.ui.roadmap.v.text_description.toPlainText()
        dc.sp.m._(self.smajor)._(self.sminor).description.v = description
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMilestoneItemActivated(self):
        if self.smajor > dc.sp.curr.major.v or \
                (self.smajor == dc.sp.curr.major.v \
                 and self.sminor > dc.sp.curr.minor.v):
            self.showAddEditMI('edit')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowTab(self):
        if dc.r.roadmap.pid.last.v == dc.spid.v: return
        dc.r.roadmap.pid.last.v = dc.spid.v
        dc.ui.roadmap.v.line_project.setText(dc.sp.name.v)
        dc.ui.roadmap_diag_add.v.line_project.setText(dc.sp.name.v)
        gl = dc.ui.roadmap.v.gridLayout_3
        gl.removeWidget(dc.ui.roadmap.v.push_milestone)
        dc.ui.roadmap.v.push_milestone.close()
        mpb = MPushButton(dc.ui.roadmap.v, self.onChangeVersionSelection)
        dc.ui.roadmap.v.push_milestone = mpb
        gl.addWidget(mpb, 0, 1, 1, 1)
        dc.ui.roadmap.v.label_2.setBuddy(mpb)
        self.reloadTable()
        major = dc.ui.roadmap.v.push_milestone.next_x
        minor = dc.ui.roadmap.v.push_milestone.next_y
        self.onChangeVersionSelection(major, minor)
        d = dc.ui.roadmap_diag_add.v
        d.radio_medium.setChecked(True)
        d.radio_feature.setChecked(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMIClicked(self):
        sumopen = 0
        for itemid in dc.sp.m._(self.smajor)._(self.sminor).idx.v:
            if dc.sp.mi._(itemid).status.v == 'Open':
                sumopen += 1
        if sumopen == 1:
            self.closeMilestone()
        else:
            self.closeMI(self.getSelectedItemId())
            self.reloadTable()
        # FIXME: move re-open to dedicated method and add dedicated control
        """
        if status == 'Closed':
            self.reopenMI(self.getSelectedItemId())
        dc.m.project.v.touchProject()
        self.onChangeVersionSelection(self.smajor, self.sminor)
        """
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeMilestone(self):
        sumopen = 0
        for itemid in dc.sp.m._(self.smajor)._(self.sminor+1).idx.v:
            if dc.sp.mi._(itemid).status.v == 'Open':
                sumopen += 1
        if sumopen:
            dc.ui.roadmap_diag_finalize.v.push_finalize_major.setEnabled(False)
        else:
            dc.ui.roadmap_diag_finalize.v.push_finalize_major.setEnabled(True)
        dc.ui.roadmap_diag_finalize.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMinorMilestone(self):
        self.closeMI(self.getSelectedItemId())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMajorMilestone(self):
        self.closeMI(self.getSelectedItemId())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadMilestoneButton(self, targetw='root'):
        if targetw == 'root':
            ui = dc.ui.roadmap.v
            ui.gridLayout_3.removeWidget(ui.push_milestone)
            ui.push_milestone.hide()
            ui.push_milestone.close()
            ui.push_milestone = MPushButton(ui, self.onChangeVersionSelection,
                                            self.smajor, self.sminor)
            ui.gridLayout_3.addWidget(ui.push_milestone, 0, 1, 1, 1)
            ui.label_2.setBuddy(ui.push_milestone)
        elif targetw == 'diag_new_edit':
            diag = dc.ui.roadmap_diag_add.v
            diag.gridLayout_2.removeWidget(diag.push_target)
            diag.push_target.close()
            diag.push_target \
                    = MPushButton(diag,None,self.smajor, self.sminor,True)
            diag.gridLayout_2.addWidget(diag.push_target, 1, 1, 1, 1);
            diag.label_3.setBuddy(diag.push_target)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onChangeVersionSelection(self, major, minor):
        self.smajor = major
        self.sminor = minor
        description = dc.sp.m._(major)._(minor).description.v
        dc.ui.roadmap.v.text_description.setPlainText(description)
        self.reloadMilestoneButton('root')
        self.reloadTable()
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
        for filter_name in filters:
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
        for filter_name in filters:
            dc.ui.roadmap.v.__dict__['check_{}'.format(filter_name)].setChecked(
                    dc.c.roadmap._('show_{}'.format(filter_name)).v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self):
        if not isinstance(dc.ui.roadmap.v.push_milestone, MPushButton):
            return
        self.init = True
        self.saveLayout()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        dc.ui.roadmap.v.push_close.setText('&Close Item')
        self.smajor, self.sminor = dc.ui.roadmap.v.push_milestone.getVersion()
        filters = [key[6:] for key in dc.ui.roadmap.v.__dict__.keys() \
                        if key.startswith('check')]
        filter_status = set()
        for name in filters:
            if dc.ui.roadmap.v.__dict__['check_'+name].isChecked():
                filter_status.add(name)
        for miid in dc.sp.m._(self.smajor)._(self.sminor).idx.v:
            md = dc.sp.mi._(miid)
            if not {md.itype.v.lower(), md.status.v.lower(),
                    md.category.v.lower(), md.priority.v.lower()} \
                .issubset(filter_status): continue
            self.model.insertRow(0, [
                QStandardItem(str(miid).zfill(4)),
                QStandardItem(md.name.v),
                QStandardItem(md.itype.v),
                QStandardItem(md.status.v),
                QStandardItem(md.category.v),
                QStandardItem(md.priority.v),
                QStandardItem(convert(md.created.v)),
                QStandardItem(convert(md.modified.v)) ])
        self.init = False
        # only enable controls for future milestones
        if self.model.rowCount() > 0:
            ma, mi = dc.sp.curr.major.v, dc.sp.curr.minor.v
            if self.smajor > ma or (self.smajor == ma and self.sminor > mi):
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
                    = dc.spro.v['mi_index'][item_id]
            tx, ty = tmajor, minorIndex(tmajor, tminor)
            item = dc.spro.v\
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
            self.addMI(tmajor, tminor, ri_type, category,
                    name, priority, description)
        if mode == 'edit':
            self.editMI(tmajor, tminor, self.getSelectedItemId(),
                     ri_type, category, name, priority, description)
        self.reloadMilestoneButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDeleteMIClicked(self):
        self.deleteMI(self.getSelectedItemId())
        self.reloadMilestoneButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

