#!/usr/bin/env python3

import os, sys, pprint

TEST = True

data = {}

def AddRootEntry(name, entrytype, status, category, priority, challenge, version, lastchange, code):

	"""
	Explanation and stuff..
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

if TEST:
	AddRootEntry(name='test', entrytype='spark', status='none', category='tool',
	             priority=1, challenge=3, version='0.0.0', lastchange=1350571150, code=True)
	AddRootEntry(name='test2', entrytype='spark', status='none', category='protocol',
	             priority=1, challenge=2, version='0.0.0', lastchange=1350571153, code=True)
	print(data)

