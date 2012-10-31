#! /usr/bin/env python3

"""
Application Name: 	Nelia
Component:			Main loop

This file contains the entry point and main loop for
the Nelia applicaiton.
"""

import sys
from PySide import QtGui
from mainwindow import MainWindow


if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv) 
    main_window = MainWindow()
    main_window.ui.show()
    sys.exit(application.exec_())


# vim: set ts=4 sw=4 ai si expandtab:

