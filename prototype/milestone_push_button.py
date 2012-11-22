#! /usr/bin/env python3

# TODO: add version symbols (completed, current, open)

from PySide.QtCore import *
from PySide.QtGui import *
import sys, os, time, re, pprint

class MilestonePushButton(QPushButton):

    """
        This class contains a push button with menu that is populating from the nelia
        savdat data structure.

        To create this class, you should initialize it with the label, parent and milestone
        data. changeHandler should accept two parameters: major and minor version (int)

        Like this:

            myButton = MilestonePushButton(parent, data, changeHandler)
            
        To reset the data (example on load, use the reset method) and set it to v0.1:

            myButton.reset(new_data, (0,1))
    """

    def __init__(self, parent, data, changeHandler=None):

        """
            label: initial label to be displayed
            parent: widget parent
            data:   milestone data (from base savdat['roadmap'][pid])
            changeHandler: function to be called when selection is changed
        """

        super().__init__('None', parent)

        self.menuRoot = QMenu('root', self)
        self.setMenu(self.menuRoot)
        
        self.data = data
        self.rundat = {}                # this is class internal
        self.changeHandler = changeHandler
        
        self.setGeometry(0,0,250,30)
        
        self.reset(self.data, (0,1))         # select version 0.1 by default

    def milestoneSelectionChanged(self):

        """
            This callback is invoked when a milestone is selected.
        """
        # TODO: determine if newly selected milestone == old one, only update on new milestone
        # TODO: extract major and minor version, call change handler if required with these parameters

        self.setText(self.sender().text())
        # any external hook goes here, like parent widget update

    def reset(self, data, selection=None):

        """
            Rebuild widget with data. Used during initialization, loading new data
            or chaning feature / issue status / completing milestone.

            data: changed data
            selection: tuple with major and minor version for selected item
        """

        self.populateMenu(data, selection)    

    def populateMenu(self, data, selection):

        """
            Compute and build menu for the push button.
        """

        # filter away meta information
        version_data = {}
        for key in data:
            if isinstance(key, int):
                version_data[key] = data[key]

        # iterate through major versions
        for major in range(len(version_data)):

            self.rundat[major] = {}
            afo = afc = aio = aic = 0   # major version feature tracker
            maxst = version_data[major]
            for minor in range(len(version_data[major])):

                if major == 0: minor += 1
                self.rundat[major][minor] = {}
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
                action = QAction(label, mw)
                action.triggered.connect(self.milestoneSelectionChanged)
                self.rundat[major][minor]['action'] = action

            menu = QMenu('v{}.x   f:{}/{}   i:{}/{}'.format(major, afo, afo+afc, aio, aio+aic), self)
            self.rundat[major]['menu'] = menu
            for minor in self.rundat[major]:

                if not isinstance(minor, int): continue
                action = self.rundat[major][minor]['action']
                menu.addAction(action)

            self.menuRoot.addMenu(menu)


if __name__ == '__main__':

    # test

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

    pushButton = MilestonePushButton(mw, data[0])
    mw.show()

    sys.exit(app.exec_())

