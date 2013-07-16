# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import sys
from datacore import dc, _dcdump
from milestonecontrol import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = QApplication(sys.argv)
def log(msg):
    print(msg)
    dc.ui.v.xx_debug.appendPlainText(msg)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def on_add_feature():
    log('adding feature')
    dc.ctrl.v.add_milestone_item(
        0, 1, 'test', 'test', 'feature', 0, 'none')
    log(_dcdump())
def on_add_issue():
    log('adding issue')
    dc.ctrl.v.add_milestone_item(
        0, 1, 'test', 'test', 'issue', 0, 'none')
    log(_dcdump())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def on_close_feature():
    log('closing feature')
    flist = []
    for α in dc.sp.m._0._1.index.v:
        if dc.sp.m.mi._(α).mi_type.v == 'feature' \
                and dc.sp.m.mi._(α).status.v == 'open':
            flist.append(α)
    log('list of feature id\'s in the selected milestone: {}'.format(flist))
    dc.ctrl.v.close_milestone_item(flist[0])
    log(_dcdump())
def on_close_issue():
    log('closing issue')
    flist = []
    for α in dc.sp.m._0._1.index.v:
        if dc.sp.m.mi._(α).mi_type.v == 'issue' \
                and dc.sp.m.mi._(α).status.v == 'open':
            flist.append(α)
    log('list of issue id\'s in the selected milestone: {}'.format(flist))
    dc.ctrl.v.close_milestone_item(flist[0])
    log(_dcdump())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def on_delete_feature():
    log('deleting feature')
def on_delete_issue():
    log('deleting issue')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def on_move_feature():
    log('moving feature')
def on_move_issue():
    log('moving issue')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def on_run_sequence():
    log('running sequence')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def closeMinorMilestone():
    log('closing minor milestone')
def closeMajorMilestone():
    log('closing major milestone')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
loader = QtUiTools.QUiLoader()
f = QFile('milestonecontrol/test.ui')
f.open(QFile.ReadOnly)
ui = dc.ui.v = loader.load(f)
f.close()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc.ui.v.xx_add_feature	 .clicked.connect   (on_add_feature)
dc.ui.v.xx_add_issue	 .clicked.connect   (on_add_issue)
dc.ui.v.xx_close_feature .clicked.connect   (on_close_feature)
dc.ui.v.xx_close_issue	 .clicked.connect   (on_close_issue)
dc.ui.v.xx_delete_feature.clicked.connect   (on_delete_feature)
dc.ui.v.xx_delete_issue	 .clicked.connect   (on_delete_issue)
dc.ui.v.xx_move_feature	 .clicked.connect   (on_move_feature)
dc.ui.v.xx_move_issue	 .clicked.connect   (on_move_issue)
dc.ui.v.xx_run_sequence	 .clicked.connect   (on_run_sequence)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc.ctrl.v = MilestoneControl()
dc.ctrl.v.setup_new()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO: load MPBs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc.ui.v.xx_selection_layout.removeWidget(dc.ui.v.xx_selection)
dc.ui.v.xx_selection.close()
dc.ui.v.xx_selection = MilestoneButton(dc.ui.v.xx_selection_container, 0, 1)
dc.ui.v.xx_selection_layout.addWidget(dc.ui.v.xx_selection, 0, 1, 1, 1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if sys.argv[1] == '--auto':
    print('running automatic mode')
    on_run_sequence()
if sys.argv[1] == '--gui':
    print('running gui mode')
    dc.ui.v.show()
    sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

