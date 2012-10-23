#!/usr/bin/env python3

# ---------------- import modules -------------------

import os, sys, pprint
from PySide.QtCore import *
from PySide.QtGui import *

# ---------------- create global data container ---------------------

data = {}

# ----------------- define some functions that we'll need -------------------

def AddRootEntry(name, entrytype, status, category, priority, challenge, version, lastchange, code):

	"""
	Add a root entry (that is displayed on the start page) to the global data structure).

	entrytype = spark, project, product, archive
	status = none, planned, scheduled, active, maintain, decommission
	category = tool, application, library, protocol, other
	priority = 0-10
	challenge = 0-10
	version = major.minor.patch (1.3.2)
	lastchange = last edit date (int)
	code = boolean
	"""

	if name in data:
		return False
	
	data[name] = {  'entrytype' : entrytype,
			'status' : status,
			'category' : category,
			'priority' : priority,
			'challenge' : challenge,
			'version' : version,
			'lastchange' : lastchange,
			'code' : code }
	return data[name]


# ------------------ MAIN LOGIC ------------------------

AddRootEntry(name='test', entrytype='spark', status='none', category='tool',
	priority=1, challenge=3, version='0.0.0', lastchange=1350571150, code=True)
AddRootEntry(name='test2', entrytype='spark', status='none', category='protocol',
	priority=1, challenge=2, version='0.0.0', lastchange=1350571153, code=True)

# ------------------ GUI stuff ---------------------------
application = QApplication(sys.argv) 

mainwindow = QMainWindow()
mainwindow.setWindowTitle('foo')

# XXX: we are building a model mapping module, see tmodmap.py

mainlisting = QTableView()


# ------------------- show and run -----------------------
mainwindow.show()
sys.exit(application.exec_())

# vim: set ts=8 sw=8 noexpandtab:

