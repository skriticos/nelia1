#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
import sys, os, time, re, pprint

class MPushButton(QPushButton):

    def __init__(self, parent):

        super().__init__(parent)

    def setData(self, data, version):

        pass

    def selectionChanged(self):

        pass

if __name__ == "__main__":

    data = \
        {0: {0: {1: {'fc': {},
                     'fo': {1: {'completed': 0,
                                'created': 1353437574,
                                'description': 'bar',
                                'name': 'foo',
                                'priority': 50,
                                'target': [0, 1],
                                'type': 'primary'},
                            2: {'completed': 0,
                                'created': 1353437587,
                                'description': '',
                                'name': 'blah',
                                'priority': 50,
                                'target': [0, 1],
                                'type': 'primary'}},
                     'ic': {},
                     'io': {}},
                 2: {'fc': {}, 'fo': {}, 'ic': {}, 'io': {}}},
             1: {0: {'fc': {}, 'fo': {}, 'ic': {}, 'io': {}}},
             'current_milestone': [0, 0],
             'last_feature_id': 2,
             'last_issue_id': 0,
             'last_major': 1}}

    app = QApplication(sys.argv)
    mw = QMainWindow()
    mw.setGeometry(100, 100, 400, 50)

    pushButton = MPushButton(mw)
    pushButton.setData(data[0], (0,1))
    mw.show()

    sys.exit(app.exec_())

