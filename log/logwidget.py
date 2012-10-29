#! /usr/bin/env python3

"""
    Name:       logwidget.py
    Purpose:    A widegt that shows the logs for a project.
    Input:      When shown, it is populated with the log data for a particular
                project.
    Fields:     1. Auto generated logs from activities generated in Nelia.
                2. Log entry mask, to add new, manual log entries (general).
    Notes:      1. Might be a good place to put statistics in?
                2. Still have to figure out the workflow (single, muliple..).
                3. Might be a good idea to put this in a detachable tab?
"""


import sys
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *


class LogWidget(QWidget):


    def __init__(self, parent=None):

        super().__init__(parent)
        self.data = {}

        loader = QUiLoader()
        uifile = QFile('logwidget.ui')
        uifile.open(QFile.ReadOnly)
        self.ui = loader.load(uifile, self)
        uifile.close()


    def add_manual_log(self):

        pass


    def add_log(self, log_message):

        pass


    def refresh_view(self, data):

        pass


if __name__ == '__main__':
    application = QApplication(sys.argv) 
    w = LogWidget()
    w.show()
    sys.exit(application.exec_())


# vim: set ts=4 sw=4 ai si expandtab:

