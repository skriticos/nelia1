#! /usr/bin/env python3

from PySide.QtCore import *
from PySide.QtGui import *
from pprint import pprint
import sys, os, time, re

class MPushButton(QPushButton):

    """
        This class contains a push button with menu that is populating from the nelia
        savdat data structure.

        To create this class, you should initialize it with the label, parent and milestone
        data.

        Note: once you have created this button, you'll have to set data, or it stays
              empty.

    """

    def __init__(self, parent=None, change_callback=None):

        super().__init__(parent)

        self.parent = parent
        self.setText('        no data        ')
        self.menuRoot = QMenu(self)
        self.change_callback = change_callback

    def setData(self, data, version):

        # select the next minor version
        self.selected = data['current_milestone'][0], data['current_milestone'][1]+1
        
        self.menuRoot.clear()

        # filter out milestone meta information
        version_data = {}

        for key in data:

            if isinstance(key, int):
                version_data[key] = data[key]
        
        for major in range(len(version_data)):

            afo = afc = aio = aic = 0   # major version feature tracker
            menu = QMenu(self)

            for minor in range(len(version_data[major])):

                if major == 0:
                    minor += 1

                fo = af = io = ic = 0
                minst = version_data[major][minor]

                fo = len(minst['fo'])
                fc = len(minst['fc'])
                io = len(minst['io'])
                ic = len(minst['ic'])
                afo += fo
                afc += fc
                aio += io
                aic += ic

                majd = major - data['current_milestone'][0] # milestone delta
                mind = 0
                sign = '+'
                # compute minor delta
                if majd == 0:
                    mind = minor
                elif majd > 0:
                    mind = minor - data['current_milestone'][1]
                else:
                    mind = data['current_milestone'][1] + (len(data[major]) - minor)
                    sign = '-'

                label = 'v{}.{}   {}{}.{}   f:{}/{}   i:{}/{}'.format(major, minor, sign, majd, mind, fo, fo+fc, io, io+ic)
                if major == self.selected[0] and minor == self.selected[1]:
                    self.setText(label)

                import images
                icon = QIcon('open.png')
                action = QAction(label, self)
                action.setIcon(icon)
                action.triggered.connect(self.selectionChanged)
                menu.addAction(action)

            menu.setTitle('v{}.x   f:{}/{}   i:{}/{}'.format(major, afo, afo+afc, aio, aio+aic))
            self.menuRoot.addMenu(menu)
        
        self.setMenu(self.menuRoot)

    def selectionChanged(self):

        """
            This callback is invoked when a milestone is selected.
        """
        # TODO: determine if newly selected milestone == old one, only update on new milestone

        old_text = self.text()
        text = self.sender().text()
        if old_text == text:
            return

        self.setText(text)
        
        if self.change_callback:
            version_text = text.split(' ')[0][1:].split('.')
            for i,item in enumerate(version_text):
                version_text[i] = int(version_text[i])
            self.change_callback((version_text[0], version_text[1]))


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

    pushButton = MPushButton()
    pushButton.setData(data[0], (0,1))
    pushButton.show()

    sys.exit(app.exec_())

