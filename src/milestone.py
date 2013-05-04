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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def versionToIndex(major, minor):
    # there is no 0.0 milestone, first one is 0.1. there is 1.0 though
    if major > 0:
        return major, minor
    else:
        return major, minor - 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _indexToVersion(x, y):

    if x > 0:
        return x, y
    else:
        return x, y + 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _addMilestone(major, minor):

    x, y = versionToIndex(major, minor)

    if y == 0:
        data.spro['milestone'].append(
           [{'description': '', 'm': '{}.{}'.format(major, minor),
              'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}])
    else:
        data.spro['milestone'][x].append(
            {'description': '', 'm': '{}.{}'.format(major, minor),
             'fo': {}, 'fc': {}, 'io': {}, 'ic': {}})

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _removeMilestone(major, minor):

    x, y = versionToIndex(major, minor)

    # n.0 deletes major milestone
    if y == 0: del data.spro['milestone'][x]
    # otherwise we are only deleting minor milestone
    else: del data.spro['milestone'][x][y]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _updateMilestoneTree():

    '''
        If an item is created/moved to/from the milestone graph edge,
        edge graph has to be updated.
    '''

    cmajor, cminor = data.spro['meta']['current_milestone']
    cx, cy = versionToIndex(cmajor, cminor)

    for x in range(len(data.spro['milestone'])):

        # if we have removed the last major branch before, we want to get
        # out
        if x == len(data.spro['milestone']):
            break

        # check for new edge item
        last_index = len(data.spro['milestone'][x]) - 1
        major, minor = _indexToVersion(x, last_index)
        item_count = (
                len(data.spro['milestone'][x][last_index]['fo']) +
                len(data.spro['milestone'][x][last_index]['fc']) +
                len(data.spro['milestone'][x][last_index]['io']) +
                len(data.spro['milestone'][x][last_index]['ic']))
        if item_count > 0:
            if minor == 0:
                _addMilestone(major, 1)
                _addMilestone(major + 1, 0)
            else:
                _addMilestone(major, minor + 1)

        # check for removed edge item
        if len(data.spro['milestone'][x]) > 1:
            index = len(data.spro['milestone'][x]) - 2
            major, minor = _indexToVersion(x, index)
            item_count = (
                    len(data.spro['milestone'][x][index]['fo']) +
                    len(data.spro['milestone'][x][index]['fc']) +
                    len(data.spro['milestone'][x][index]['io']) +
                    len(data.spro['milestone'][x][index]['ic']))
            if item_count == 0:
                if minor == 0:
                    _removeMilestone(major, 1)
                    _removeMilestone(major + 1, 0)
                else:
                    _removeMilestone(major, minor + 1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _getItemData(item_id):

    ma, mi, fioc = data.spro['mi_index'][item_id]
    x, y = versionToIndex(ma, mi)

    item = data.spro['milestone'][x][y][fioc][item_id]

    if   fioc[0] == 'f': itype  = 'Feature'
    elif fioc[0] == 'i': itype  = 'Issue'
    if   fioc[1] == 'o': status = 'Open'
    elif fioc[1] == 'c': status = 'Closed'

    return {'major': ma,
            'minor': mi,
            'x': x,
            'y': y,
            'name': item['name'],
            'itype': itype,
            'icat': item['icat'],
            'priority': item['priority'],
            'description': item['description'],
            'status': status,
            'fioc': fioc}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _getAttribute(item_id, attr_name):

    idat = _getItemData(item_id)
    return idat[attr_name]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _setAttribute(item_id, attr_name, value):

    idat = _getItemData(item_id)
    data.spro['milestone'][idat['x']][idat['y']] \
           [idat['fioc']][item_id][attr_name] = value

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _touchItem(item_id):

    _setAttribute(item_id, 'modified', int(time.time()))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def addItem(major, minor, itype, icat, name, priority,
            description, status='Open'):

    print(major, minor, itype, icat, name, priority)

    item_id = data.spro['meta']['next_miid']

    new_item = {'name': name,
                'icat': icat,
                'priority': priority,
                'description': description,
                'created': int(time.time())}

    x, y = versionToIndex(major, minor)
    if   itype == 'Feature': fioc = 'fo'
    elif itype == 'Issue':   fioc = 'io'

    data.spro['milestone'][x][y][fioc][item_id] = new_item
    data.spro['mi_index'][item_id] = (major, minor, fioc)

    data.spro['meta']['next_miid'] += 1
    _touchItem(item_id)

    _updateMilestoneTree()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def editItem(major, minor, item_id, itype, icat, name, priority, description):

    idat = _getItemData(item_id)
    for k, v in (('icat', icat),
                 ('name', name),
                 ('priority', priority),
                 ('description', description)):
        _setAttribute(item_id, k, v)

    if itype != idat['itype'] or major != idat['major'] \
            or minor != idat['minor']:
        _moveItem(item_id, major, minor, itype, idat['status'])

    _touchItem(item_id)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _moveItem(item_id, new_major, new_minor, itype=None, status=None):

    idat = _getItemData(item_id)
    nx, ny = versionToIndex(new_major, new_minor)

    if not itype and not status:
        nfioc = idat['fioc']
    else:
        if itype == 'Feature':
            if not status:
                nfioc = 'f' + idat['fioc'][1]
            elif status == 'Open':
                nfioc = 'fo'
            elif status == 'Closed':
                nfioc = 'fc'
        elif itype == 'Issue':
            if not status:
                nfioc = 'i' + idat['fioc'][1]
            elif status == 'Open':
                nfioc = 'io'
            elif status == 'Closed':
                nfioc = 'ic'

    item = data.spro['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    data.spro['milestone'][nx][ny][nfioc][item_id] = item
    del data.spro['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    data.spro['mi_index'][item_id] = (new_major, new_minor, nfioc)
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
    del data.spro['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
    del data.spro['mi_index'][item_id]
    _updateMilestoneTree()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

