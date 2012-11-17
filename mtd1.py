#! /usr/bin/env python3

"""
	Test data for milestones.
"""
a = {
	'current_milestone': 5,
	'next_new_milestone': 7,
	'next_new_feature': 10,
	'next_new_issue': 5,
	1: {'name':'0.1', 'next':3,
		'features': {0: {'completed': 1}, 1: {'completed': 1} },
		'issues': {0: {'completed': 1}, 1: {'completed': 1} } },
	2: {'name':'2.0', 'next':5,
		'features': {10: {'completed': 0}, 14: {'completed': 0} },
		'issues': {7: {'completed': 0}, 8: {'completed': 0} } },
	3: {'name': '1.1', 'next': 5,
		'features': { 2: {'completed': 1}, 3: {'completed': 1} },
		'issues': { 2: {'completed': 1}, 3: {'completed': 1} } },
	5: {'name': '1.3', 'next': 2,
		'features': { 11: {'completed': 1}, 13: {'completed': 0} },
		'issues': { 9: {'completed': 0}, 10: {'completed': 1} } }
}

if __name__ == '__main__':
	import pprint
	pprint.pprint(a)

