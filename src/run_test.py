#! /usr/bin/env python3
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys, PySide, mainwindow
from datacore import *
from datacore import _dcNode
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
log('***** STARTING UP APPLICATION *****')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = PySide.QtGui.QApplication(sys.argv)
mainwindow.MainWindow(sys.argv, app)
dc.ui.main.v.hide()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
log('****** TEST CASE "CREATE NEW PROJECT" STARTING *****')
diag = dc.ui.project_diag_new.v
diag.line_name.setText('test project')
diag.text_description.setPlainText('test project desciption')
dc.m.project.v.onNewProject()
assert(dc.s.nextpid.v == 2)
assert(dc.spid.v == 1)
assert(dc.s._1.nextlid.v == 1)
assert(dc.s._1.name.v == 'test project')
assert(dc.s._1.category.v == 'Development')
assert(dc.s._1.status.v == 'Spark')
assert(dc.s._1.ptype.v == 'Utility')
assert(dc.s._1.priority.v == 0)
assert(dc.s._1.challenge.v == 0)
assert(dc.s._1.description.v == 'test project desciption')
assert(dc.s._1.m.mi.nextid.v == 1)
assert(dc.s._1.m.mi.index.v == {})
assert(dc.s._1.m.mi.selected.v == None)
assert(dc.s._1.m.active.v == (0, 1))
assert(dc.s._1.m.selected.v == (0, 1))
assert(dc.s._1.m.index.v == {0, 1})
assert(dc.s._1.m._0.index.v == {1})
assert(dc.s._1.m._0._1.index.v == set())
assert(dc.s._1.m._0._1.detail.v == '')
assert(dc.s._1.m._1.index.v == {0})
assert(dc.s._1.m._1._0.index.v == set())
assert(dc.s._1.m._1._0.detail.v == '')
log('****** TEST CASE "CREATE EDIT PROJECT" STARTING *****')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
log('***** TEST RUN MAIN LOOP AND SHUT DOWN *****')
def quitApp():
    dc.ui.main.v.close()
timer = PySide.QtCore.QTimer()
timer.start(100)
timer.timeout.connect(quitApp)
app.exec_()
log('***** BYE BYE *****')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

