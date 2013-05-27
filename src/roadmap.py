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
        self.init = True
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(headers)
        self.table = dc.ui.roadmap.v.table
        self.table.setModel(self.model)
        selmod = self.selection_model = self.table.selectionModel()
        self.horizontal_header = self.table.horizontalHeader()
        win = dc.ui.roadmap.v
        win.push_add_feature.clicked.connect(self.onAddFeatureClicked)
        win.push_add_issue.clicked.connect(self.onAddIssueClicked)
        dc.ui.roadmap_diag_add.v.accepted.connect(self.onSubmitNewMI)
        dc.ui.roadmap_diag_edit.v.accepted.connect(self.onSubmitEditMI)
        for f in filters:
            widget = win.__dict__['check_{}'.format(f)]
            widget.stateChanged.connect(self.reloadTable)
        win.push_delete.clicked.connect(self.onDeleteMIClicked)
        win.push_edit.clicked.connect(self.onEditMIClicked)
        win.push_close.clicked.connect(self.onCloseMIClicked)
        win.push_reopen.clicked.connect(self.onReopenMIClicked)
        dfin = dc.ui.roadmap_diag_finalize.v
        dfin.push_finalize_major.clicked.connect(self.onCloseMajorMs)
        dfin.push_finalize_minor.clicked.connect(self.onCloseMinorMs)
        selmod.selectionChanged.connect(self.onItemSelectionChanged)
        win.text_description.textChanged.connect(self.onMsDescChanged)
        self.table.activated.connect(self.onMIActivated)
        for w in ['label_selected', 'push_edit', 'push_delete', 'push_close',
                  'push_reopen']:
            dc.ui.roadmap.v.__dict__[w].hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onShowTab(self):
        if dc.r.roadmap.pid.last.v == dc.spid.v: return
        dc.r.roadmap.pid.last.v = dc.spid.v
        self.smiid = 0
        dc.ui.roadmap.v.line_project.setText(dc.sp.name.v)
        dc.ui.roadmap_diag_add.v.line_project.setText(dc.sp.name.v)
        dc.ui.roadmap_diag_edit.v.line_project.setText(dc.sp.name.v)
        self.smajor, self.sminor = dc.sp.curr.major.v, dc.sp.curr.minor.v+1
        description = dc.sp.m._(self.smajor)._(self.sminor).description.v
        dc.ui.roadmap.v.text_description.setPlainText(description)
        self.updateRootMPushButton()
        self.reloadTable()
        d = dc.ui.roadmap_diag_add.v
        d.radio_medium.setChecked(True)
        d.radio_feature.setChecked(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAddFeatureClicked(self):
        dc.ui.roadmap_diag_add.v.radio_feature.setChecked(True)
        dc.ui.roadmap_diag_add.v.line_name.clear()
        dc.ui.roadmap_diag_add.v.text_description.clear()
        self.updateDiagMPushButton()
        dc.ui.roadmap_diag_add.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onAddIssueClicked(self):
        dc.ui.roadmap_diag_add.v.radio_issue.setChecked(True)
        dc.ui.roadmap_diag_add.v.line_name.clear()
        dc.ui.roadmap_diag_add.v.text_description.clear()
        self.updateDiagMPushButton()
        dc.ui.roadmap_diag_add.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onEditMIClicked(self):
        diag = dc.ui.roadmap_diag_edit.v
        node = dc.sp.mi._(self.smiid)
        if node.itype.v == 'Feature': diag.radio_feature.setChecked(True)
        if node.itype.v == 'Issue':   diag.radio_issue.setChecked(True)
        itype, prio, cat = node.itype.v, node.priority.v, node.category.v
        if itype == 'Feature': diag.radio_feature.setChecked(True)
        if itype == 'Issue':   diag.radio_issue.setChecked(True)
        if prio == 'Low':    diag.radio_low.setChecked(True)
        if prio == 'Medium': diag.radio_medium.setChecked(True)
        if prio == 'High':   diag.radio_high.setChecked(True)
        if cat == 'Core':         diag.radio_core.setChecked(True)
        if cat == 'Auxiliary':    diag.radio_auxiliary.setChecked(True)
        if cat == 'Security':     diag.radio_security.setChecked(True)
        if cat == 'Corrective':   diag.radio_corrective.setChecked(True)
        if cat == 'Architecture': diag.radio_architecture.setChecked(True)
        if cat == 'Refactor':     diag.radio_refactor.setChecked(True)
        diag.line_name.setText(node.name.v)
        diag.text_description.setPlainText(node.description.v)
        self.updateDiagMPushButton()
        diag.show()
        diag.line_name.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMIActivated(self):
        cma, cmi = dc.sp.curr.major.v, dc.sp.curr.minor.v
        if self.smajor > cma or (self.smajor == cma and self.sminor > cmi):
            dc.ui.roadmap_diag_edit.v.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSubmitNewMI(self):
        diag = dc.ui.roadmap_diag_add.v
        if diag.radio_feature.isChecked(): itype = 'Feature'
        if diag.radio_issue.isChecked():   itype = 'Issue'
        if diag.radio_medium.isChecked(): priority = 'Medium'
        elif diag.radio_high.isChecked(): priority = 'High'
        elif diag.radio_low.isChecked():  priority = 'Low'
        if diag.radio_core.isChecked():           category = 'Core'
        elif diag.radio_auxiliary.isChecked():    category = 'Auxiliary'
        elif diag.radio_security.isChecked():     category = 'Security'
        elif diag.radio_corrective.isChecked():   category = 'Corrective'
        elif diag.radio_architecture.isChecked(): category = 'Architecture'
        elif diag.radio_refactor.isChecked():     category = 'Refactor'
        tlabel = diag.push_target.text()
        major, minor = tlabel.split(' ')[3][1:].split('.')
        major, minor = int(major), int(minor)
        self.smiid = dc.sp.nextmiid.v
        dc.sp.nextmiid.v += 1
        dc.sp.midx.v[self.smiid] = major, minor
        node = dc.sp.mi._(self.smiid)
        node.name.v        = diag.line_name.text()
        node.description.v = diag.text_description.toPlainText()
        node.priority.v    = priority
        node.category.v    = category
        node.itype.v       = itype
        node.status.v      = 'Open'
        node.created.v     = node.modified.v = int(time.time())
        dc.sp.m._(major)._(minor).idx.v.add(self.smiid)
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onSubmitEditMI(self):
        diag = dc.ui.roadmap_diag_edit.v
        if diag.radio_feature.isChecked(): itype = 'Feature'
        if diag.radio_issue.isChecked():   itype = 'Issue'
        if diag.radio_medium.isChecked(): priority = 'Medium'
        elif diag.radio_high.isChecked(): priority = 'High'
        elif diag.radio_low.isChecked():  priority = 'Low'
        if diag.radio_core.isChecked():           category = 'Core'
        elif diag.radio_auxiliary.isChecked():    category = 'Auxiliary'
        elif diag.radio_security.isChecked():     category = 'Security'
        elif diag.radio_corrective.isChecked():   category = 'Corrective'
        elif diag.radio_architecture.isChecked(): category = 'Architecture'
        elif diag.radio_refactor.isChecked():     category = 'Refactor'
        tlabel = diag.push_target.text()
        major, minor = tlabel.split(' ')[3][1:].split('.')
        major, minor = int(major), int(minor)
        if (major, minor) != dc.sp.midx.v[self.smiid]:
            old_major, old_minor = dc.sp.midx.v[self.smiid]
            dc.sp.m._(old_major)._(old_minor).idx.v.remove(self.smiid)
            dc.sp.m._(major)._(minor).idx.v.add(self.smiid)
            dc.sp.midx.v[self.smiid] = major, minor
        node = dc.sp.mi._(self.smiid)
        node.itype.v       = itype
        node.name.v        = diag.line_name.text()
        node.category.v    = category
        node.priority.v    = priority
        node.description.v = diag.text_description.toPlainText()
        node.changed.v     = int(time.time())
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onDeleteMIClicked(self):
        del dc.sp.mi.__dict__['_{}'.format(self.smiid)]
        major, minor = dc.sp.midx.v[self.smiid]
        del dc.sp.midx.v[self.smiid]
        dc.sp.m._(major)._(minor).idx.v.remove(self.smiid)
        self.updateMsTree()
        self.updateRootMPushButton()
        self.reloadTable()
        dc.m.project.v.touchProject()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onItemSelectionChanged(self, item_selection):
        indexes = item_selection.indexes()
        if not indexes:
            if not len(dc.sp.m._(self.smajor)._(self.sminor).idx.v):
                for w in ['label_selected', 'push_edit', 'push_delete',
                          'push_close', 'push_reopen']:
                    dc.ui.roadmap.v.__dict__[w].hide()
            return
        for w in ['label_selected', 'push_edit', 'push_delete']:
            dc.ui.roadmap.v.__dict__[w].show()
        row = indexes[0].row()
        index = self.model.index(row, 0)
        item  = self.model.itemFromIndex(index)
        self.smiid = int(item.text())
        if dc.sp.mi._(self.smiid).status.v == 'Open':
            dc.ui.roadmap.v.push_close.show()
            dc.ui.roadmap.v.push_reopen.hide()
        if dc.sp.mi._(self.smiid).status.v == 'Closed':
            dc.ui.roadmap.v.push_close.hide()
            dc.ui.roadmap.v.push_reopen.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMsSelectionChanged(self, major, minor):
        self.smajor = major
        self.sminor = minor
        description = dc.sp.m._(major)._(minor).description.v
        dc.ui.roadmap.v.text_description.setPlainText(description)
        self.updateRootMPushButton()
        self.reloadTable()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMinorMs(self):
        dc.sp.mi._(self.smiid).status.v = 'Closed'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        if self.smajor > dc.sp.curr.major.v:
            dc.sp.curr.major.v += 1
        dc.sp.curr.minor.v += 1
        self.sminor += 1
        self.reloadTable()
        self.updateRootMPushButton()
        dc.ui.roadmap_diag_finalize.v.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMajorMs(self):
        dc.sp.mi._(self.smiid).status.v = 'Closed'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        x = max(dc.sp.m._(self.smajor).idx.v)
        dc.sp.m._(self.smajor).idx.v.remove(x)
        dc.sp.curr.minor.v += 1
        self.sminor = 0
        self.smajor = dc.sp.curr.major.v + 1
        self.reloadTable()
        self.updateRootMPushButton()
        dc.ui.roadmap_diag_finalize.v.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onMsDescChanged(self):
        if self.init: return
        description = dc.ui.roadmap.v.text_description.toPlainText()
        dc.sp.m._(self.smajor)._(self.sminor).description.v = description
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onCloseMIClicked(self):
        sumopen = 0
        ma, mi = self.smajor, self.sminor
        if ma == dc.sp.curr.major.v and mi == dc.sp.curr.minor.v+1:
            for itemid in dc.sp.m._(ma)._(mi).idx.v:
                if dc.sp.mi._(itemid).status.v == 'Open': sumopen += 1
            if sumopen == 1: self.closeMs()
        else:
            dc.sp.mi._(self.smiid).status.v = 'Closed'
            dc.sp.mi._(self.smiid).changed.v = int(time.time())
            dc.m.project.v.touchProject()
            self.reloadTable()
        self.updateRootMPushButton()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def onReopenMIClicked(self):
        dc.sp.mi._(self.smiid).status.v = 'Open'
        dc.sp.mi._(self.smiid).changed.v = int(time.time())
        dc.m.project.v.touchProject()
        self.reloadTable()
        self.updateRootMPushButton()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateMsTree(self):
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
    def closeMs(self):
        sumopen = 0
        for itemid in dc.sp.m._(self.smajor)._(self.sminor+1).idx.v:
            if dc.sp.mi._(itemid).status.v == 'Open': sumopen += 1
        diag = dc.ui.roadmap_diag_finalize.v
        if sumopen: diag.push_finalize_major.setEnabled(False)
        else:       diag.push_finalize_major.setEnabled(True)
        diag.show()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def saveLayout(self):
        dc.c.roadmap.header.width.v = list()
        for i in range(self.model.columnCount()):
            dc.c.roadmap.header.width.v.append(self.table.columnWidth(i))
        cnode   = dc.c.roadmap.sort.column
        cnode.v = self.horizontal_header.sortIndicatorSection()
        cnode   = dc.c.roadmap.sort.order
        cnode.v = self.horizontal_header.sortIndicatorOrder().__repr__()
        for f in filters:
            cnode   = dc.c.roadmap._('show_{}'.format(f))
            cnode.v = dc.ui.roadmap.v.__dict__['check_{}'.format(f)].isChecked()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def loadLayout(self):
        for index, width in enumerate(dc.c.roadmap.header.width.v):
            self.table.setColumnWidth(index, width)
        if dc.c.roadmap.sort.column.v:
            column = dc.c.roadmap.sort.column.v
            order  = convert(dc.c.roadmap.sort.order.v)
            self.horizontal_header.setSortIndicator(column, order)
        for f in filters:
            widget = dc.ui.roadmap.v.__dict__['check_{}'.format(f)]
            widget.setChecked(dc.c.roadmap._('show_{}'.format(f)).v)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reloadTable(self):
        if not dc.ui.roadmap.v.isVisible(): return
        self.init = True
        self.saveLayout()
        self.model.clear()
        self.model.setHorizontalHeaderLabels(headers)
        dc.ui.roadmap.v.push_close.setText('&Close Item')
        self.smajor, self.sminor = dc.ui.roadmap.v.push_milestone.getVersion()
        filter_status = set()
        for name in filters:
            if dc.ui.roadmap.v.__dict__['check_'+name].isChecked():
                filter_status.add(name)
        for miid in dc.sp.m._(self.smajor)._(self.sminor).idx.v:
            md = dc.sp.mi._(miid)
            if {md.itype.v.lower(), md.status.v.lower(),
                    md.category.v.lower(), md.priority.v.lower()} \
                   .issubset(filter_status):
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
        if self.model.rowCount(): self.table.selectRow(0)
        self.loadLayout()
        self.table.setFocus()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateRootMPushButton(self):
        ui = dc.ui.roadmap.v
        ui.gridLayout_3.removeWidget(ui.push_milestone)
        ui.push_milestone.hide()
        ui.push_milestone.close()
        ma, mi = self.smajor, self.sminor
        ui.push_milestone = MPushButton(ui, self.onMsSelectionChanged, ma, mi)
        ui.gridLayout_3.addWidget(ui.push_milestone, 0, 1, 1, 1)
        ui.label_2.setBuddy(ui.push_milestone)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateDiagMPushButton(self):
        diags = dc.ui.roadmap_diag_add.v, dc.ui.roadmap_diag_edit.v
        for d in diags:
            d.gridLayout_2.removeWidget(d.push_target)
            d.push_target.close()
            d.push_target = MPushButton(d, None, self.smajor, self.sminor, True)
            d.gridLayout_2.addWidget(d.push_target, 1, 1, 1, 1);
            d.label_3.setBuddy(d.push_target)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

