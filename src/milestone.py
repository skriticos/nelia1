# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# asumption: all functions in this module operate on the currently selected
#            project
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import time
from datastore import data
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def minorIndex(major, minor):
    if major is 0: return minor - 1
    return minor
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _minorVersion(x, y):
    if x is 0: return y + 1
    return y
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _getItemCount(major, minor):
    m = dc.spro.v['milestone'][major][minorIndex(major, minor)]
    return sum(len(x) for x in [m['fo'], m['fc'], m['io'], m['ic']])
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _addMilestone(major, minor):
    d = {'description': '', 'm': '{}.{}'.format(major, minor),
         'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
    if minorIndex(major, minor) is 0:
        dc.spro.v['milestone'].append([d])
    else:
        dc.spro.v['milestone'][major].append(d)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _removeMilestone(major, minor):
    if minorIndex(major, minor) is 0:
        del dc.spro.v['milestone'][major]
    else:
        del dc.spro.v['milestone'][major][minorIndex(major, minor)]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _updateMilestoneTree():
    for major in range(len(dc.spro.v['milestone'])):
        # if we have removed the last major branch before, we want to get out
        if major == len(dc.spro.v['milestone']): break
        # check for new edge item
        last_minor = _minorVersion(major, len(dc.spro.v['milestone'][major])-1)
        if _getItemCount(major, last_minor):
            if last_minor is 0:
                _addMilestone(major, 1)
                _addMilestone(major + 1, 0)
            else:
                _addMilestone(major, last_minor + 1)
        # check for removed edge item
        # TODO: check if this works if if major has to be removed
        # TODO: edge case - create a bunch of milestones, then back to start
        if len(dc.spro.v['milestone'][major]) > 1:
            before_last_minor = \
                    _minorVersion(major, len(dc.spro.v['milestone'][major])-2)
            if _getItemCount(major, before_last_minor) is 0:
                if minor == 0:
                    _removeMilestone(major, 1)
                    _removeMilestone(major + 1, 0)
                else:
                    _removeMilestone(major, minor + 1)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _getItemData(item_id):
    ma, mi, fioc = dc.spro.v['mi_index'][item_id]
    item = dc.spro.v['milestone'][ma][minorIndex(ma, mi)][fioc][item_id]
    if   fioc[0] == 'f': itype  = 'Feature'
    elif fioc[0] == 'i': itype  = 'Issue'
    if   fioc[1] == 'o': status = 'Open'
    elif fioc[1] == 'c': status = 'Closed'
    return {'major': ma, 'minor': mi, 'x': ma, 'y': minorIndex(ma, mi),
            'name': item['name'], 'itype': itype, 'icat': item['icat'],
            'priority': item['priority'], 'description': item['description'],
            'status': status, 'fioc': fioc}
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _getAttribute(item_id, attr_name):
    idat = _getItemData(item_id)
    return idat[attr_name]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _setAttribute(item_id, attr_name, value):
    idat = _getItemData(item_id)
    dc.spro.v['milestone'][idat['x']][idat['y']] \
           [idat['fioc']][item_id][attr_name] = value
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _touchItem(item_id):
    _setAttribute(item_id, 'modified', int(time.time()))
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def addItem(major, minor, itype, icat, name,priority,description,status='Open'):
    new_item = {'name': name, 'icat': icat,
                'priority': priority, 'description': description,
                'created': int(time.time())}
    if   itype == 'Feature': fioc = 'fo'
    elif itype == 'Issue':   fioc = 'io'
    y = minorIndex(major, minor)
    dc.spro.v['milestone'][major][y][fioc][dc.s._(dc.spid.v).nextmiid.v] \
            = new_item
    dc.spro.v['mi_index'][dc.s._(dc.spid.v).nextmiid.v] = (major, minor, fioc)
    _touchItem(dc.s._(dc.spid.v).nextmiid.v)
    dc.s._(dc.spid.v).nextmiid.v += 1
    _updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def editItem(major, minor, item_id, itype, icat, name, priority, description):
    idat = _getItemData(item_id)
    for k, v in (('icat', icat),
                 ('name', name),
                 ('priority', priority),
                 ('description', description)):
        _setAttribute(item_id, k, v)
    if itype!=idat['itype'] or major!=idat['major'] or minor!=idat['minor']:
        _moveItem(item_id, major, minor, itype, idat['status'])
    _touchItem(item_id)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _moveItem(item_id, new_major, new_minor, itype=None, status=None):
    idat = _getItemData(item_id)
    nx, ny = new_major, minorIndex(new_major, new_minor)
    if not itype and not status:       nfioc = idat['fioc']
    else:
        if itype == 'Feature':
            if not status:             nfioc = 'f' + idat['fioc'][1]
            elif   status == 'Open':   nfioc = 'fo'
            elif   status == 'Closed': nfioc = 'fc'
        elif itype == 'Issue':
            if not status:             nfioc = 'i' + idat['fioc'][1]
            elif   status == 'Open':   nfioc = 'io'
            elif   status == 'Closed': nfioc = 'ic'
    item = dc.spro.v['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    dc.spro.v['milestone'][nx][ny][nfioc][item_id] = item
    del dc.spro.v['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    dc.spro.v['mi_index'][item_id] = (new_major, new_minor, nfioc)
    _touchItem(item_id)
    _updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def closeItem(item_id):
    idat = _getItemData(item_id)
    _moveItem(item_id, idat['major'], idat['minor'], idat['itype'], 'Closed')
    _touchItem(item_id)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def reopenItem(item_id):
    idat = _getItemData(item_id)
    _moveItem(item_id, idat['major'], idat['minor'], idat['itype'], 'Open')
    _touchItem(item_id)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def deleteItem(item_id):
    idat = _getItemData(item_id)
    del dc.spro.v['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    del dc.spro.v['mi_index'][item_id]
    _updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

