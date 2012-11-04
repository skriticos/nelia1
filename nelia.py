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

TEST = True

if __name__ == '__main__':
    application = QtGui.QApplication(sys.argv) 
    main_window = MainWindow()
    main_window.ui.show()

    if TEST:
        # create a new root entry
        main_window.index_table_ctrl.addNewRow(
            'Test Project 1',
            'Utility',
            'Development',
            '20',
            '60')
        main_window.index_table_ctrl.view.selectRow(0)
        

    sys.exit(application.exec_())


# vim: set ts=4 sw=4 ai si expandtab:

