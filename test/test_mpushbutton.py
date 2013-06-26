import os, sys, PySide

sys.path.insert(0, 'src')

import datacore
import mainwindow
import project
import log
import mpushbutton
import project

from datacore import _dcdump
from datacore import dc

print('Testing MPushButton..')

app = PySide.QtGui.QApplication(sys.argv)
mainwindow.MainWindow(sys.argv, app)

print('setting up basic application..')
dc.m.project.v.onNewClicked()
dc.ui.project_diag_new.v.line_name.setText('test project')
dc.m.project.v.onNewProject()
dc.ui.main.v.
_dcdump(dc.sp, 'sp')

print('switching to roadmap..')
print('adding feature to 0.1..')

