# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
from PySide import QtUiTools
import sys
from datacore import dc, _dcdump
from milestonectrl import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# UI INDEX
# dc.ui.v.pushAddMi
# dc.ui.v.pushCloseMi
# dc.ui.v.pushDeleteMi
# dc.ui.v.pushRun
# dc.ui.v.testMPushButton
# dc.ui.v.pushMoveMi
# dc.ui.v.pushTargetMPB
# dc.ui.v.textResult
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
app = QApplication(sys.argv)
def log(msg):
    print(msg)
    dc.ui.v.textResult.appendPlainText(msg)
def onAddMi():
    log('adding milestone item')
def onDeleteMi():
    log('deleting milestone item')
def onCloseMi():
    log('closing milestone item')
def onMoveMi():
    log('moving milestone item')
def onRun():
    log('running test sequence')
def closeMinorMilestone():
    log('closing minor milestone')
def closeMajorMilestone():
    log('closing major milestone')
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
loader = QtUiTools.QUiLoader()
f = QFile('milestonectrl/test.ui')
f.open(QFile.ReadOnly)
ui = dc.ui.v = loader.load(f)
f.close()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ui.pushAddMi.clicked.connect(onAddMi)
ui.pushCloseMi.clicked.connect(onCloseMi)
ui.pushDeleteMi.clicked.connect(onDeleteMi)
ui.pushRun.clicked.connect(onRun)
ui.pushMoveMi.clicked.connect(onMoveMi)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO: load MPBs
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if sys.argv[1] == '--auto':
    print('running automatic mode')
    onRun()
if sys.argv[1] == '--gui':
    print('running gui mode')
    dc.ui.v.show()
    sys.exit(app.exec_())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

