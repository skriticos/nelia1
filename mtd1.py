#! /usr/bin/env python3

# TODO: add dynamic callbacks, rename button on version selection

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

from PySide.QtCore import *
from PySide.QtGui import *
import sys, os, time, re, pprint

app = QApplication(sys.argv)
mw = QMainWindow()

pushButton = QPushButton('None', mw)
menuRoot = QMenu()
pushButton.setMenu(menuRoot)

# filter away meta information
version_data = {}
for key in data[0]:
	if isinstance(key, int):
		version_data[key] = data[0][key]

rundat = {}
# iterate through major versions
for major in range(len(version_data)):
	rundat[major] = {}
	afo = afc = aio = aic = 0   # major version feature tracker
	maxst = version_data[major]
	for minor in range(len(version_data[major])):
		if major == 0: minor += 1
		rundat[major][minor] = {}
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
		action = QAction('v{}.{}   f:{}/{}   i:{}/{}'.format(major, minor, fo, fo+fc, io, io+ic), mw)
		rundat[major][minor]['action'] = action

	menu = QMenu('v{}.x   f:{}/{}   i:{}/{}'.format(major, afo, afo+afc, aio, aio+aic))
	rundat[major]['menu'] = menu
	for minor in rundat[major]:
		if not isinstance(minor, int): continue
		action = rundat[major][minor]['action']
		menu.addAction(action)
	menuRoot.addMenu(menu)

mw.show()

sys.exit(app.exec_())
















