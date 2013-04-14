# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import time
from pprint import pprint
from datastore import data

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class NxMilestone:

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def versionToIndex(self, major, minor):

        if major > 0:
            return major, minor
        else:
            return major, minor - 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def indexToVersion(self, x, y):

        if x > 0:
            return x, y
        else:
            return x, y + 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addMilestone(self, pid, major, minor):

        x, y = self.versionToIndex(major, minor)

        if y == 0:
            data.project[pid] ['milestone'].append(
                [{'description': '', 'm': '{}.{}'.format(major, minor),
                  'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}]
            )
        else:
            data.project[pid] ['milestone'] [x].append(
                {'description': '', 'm': '{}.{}'.format(major, minor),
                 'fo': {}, 'fc': {}, 'io': {}, 'ic': {}}
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def removeMilestone(self, pid, major, minor):

        x, y = self.versionToIndex(major, minor)

        # n.0 deletes major milestone
        if y == 0:
            del data.project[pid]['milestone'][x]
        # otherwise we are only deleting minor milestone
        else:
            del data.project[pid]['milestone'][x][y]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def updateMilestoneTree(self, pid):

        '''
            If an item is created/moved to/from the milestone graph edge,
            edge graph has to be updated.
        '''

        p = data.project[pid]
        cmajor, cminor = data.project[pid]['meta']['current_milestone']
        cx, cy = self.versionToIndex(cmajor, cminor)

        for x in range(len(p['milestone'])):

            # if we have removed the last major branch before, we want to get
            # out
            if x == len(p['milestone']):
                break

            # check for new edge item
            last_index = len(p['milestone'][x]) - 1
            major, minor = self.indexToVersion(x, last_index)
            item_count = (
                    len(p ['milestone'] [x] [last_index] ['fo']) +
                    len(p ['milestone'] [x] [last_index] ['fc']) +
                    len(p ['milestone'] [x] [last_index] ['io']) +
                    len(p ['milestone'] [x] [last_index] ['ic'])
            )
            if item_count > 0:
                if minor == 0:
                    self.addMilestone(pid, major, 1)
                    self.addMilestone(pid, major + 1, 0)
                else:
                    self.addMilestone(pid, major, minor + 1)

            # check for removed edge item
            if len(p['milestone'][x]) > 1:
                index = len(p['milestone'][x]) - 2
                major, minor = self.indexToVersion(x, index)
                item_count = (
                        len(p ['milestone'] [x] [index] ['fo']) +
                        len(p ['milestone'] [x] [index] ['fc']) +
                        len(p ['milestone'] [x] [index] ['io']) +
                        len(p ['milestone'] [x] [index] ['ic'])
                )
                if item_count == 0:
                    if minor == 0:
                        self.removeMilestone(pid, major, 1)
                        self.removeMilestone(pid, major + 1, 0)
                    else:
                        self.removeMilestone(pid, major, minor + 1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getItemData(self, pid, item_id):

        p = data.project[pid]
        ma, mi, fioc = p['ri_index'] [item_id]
        x, y = self.versionToIndex(ma, mi)

        item = p['milestone'] [x] [y] [fioc] [item_id]

        if fioc[0] == 'f':
            itype = 'Feature'
        elif fioc[0] == 'i':
            itype = 'Issue'
        if fioc[1] == 'o':
            status = 'Open'
        elif fioc[1] == 'c':
            status = 'Closed'

        return {
            'major': ma,
            'minor': mi,
            'x': x,
            'y': y,
            'name': item['name'],
            'itype': itype,
            'icat': item['icat'],
            'priority': item['priority'],
            'description': item['description'],
            'status': status,
            'fioc': fioc
        }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getAttribute(self, pid, item_id, attr_name):

        idat = self.getItemData(pid, itme_id)
        return idat[attr_name]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def setAttibute(self, pid, item_id, attr_name, value):

        idat = self.getItemData(pid, item_id)
        data.project[pid] ['milestone'] [idat['x']] [idat['y']] \
                [idat['fioc']] [item_id] [attr_name] = value

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def touchItem(self, pid, item_id):

        self.setAttibute(pid, item_id, 'modified', int(time.time()))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def addItem(self, pid, major, minor, itype, icat, name, priority,
                description, status='Open'):

        item_id = data.project[pid] ['meta'] ['last_roadmap_item'] + 1

        new_item = {
            'name': name,
            'icat': icat,
            'priority': priority,
            'description': description,
            'created': int(time.time()),
        }

        x, y = self.versionToIndex(major, minor)
        if itype == 'Feature':
            fioc = 'fo'
        elif itype == 'Issue':
            fioc = 'io'

        data.project[pid] ['milestone'] [x] [y] [fioc] [item_id] = new_item
        data.project[pid] ['ri_index'] [item_id] = (major, minor, fioc)

        data.project[pid] ['meta'] ['last_roadmap_item'] += 1
        self.touchItem(pid, item_id)

        self.updateMilestoneTree(pid)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def editItem(self, pid, major, minor, item_id, itype, icat, name, priority,
                 description):

        idat = self.getItemData(pid, item_id)
        for k, v in (
            ('icat', icat),
            ('name', name),
            ('priority', priority),
            ('description', description)
        ):
            self.setAttibute(pid, item_id, k, v)

        if itype != idat['itype'] or major != idat['major'] \
           or minor != idat['minor']:
            self.moveItem(pid, item_id, major, minor, itype, idat['status'])

        self.touchItem(pid, item_id)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def moveItem(self, pid, item_id, new_major, new_minor, itype=None,
                 status=None):

        idat = self.getItemData(pid, item_id)
        nx, ny = self.versionToIndex(new_major, new_minor)

        if not itype and not status:
            nfioc = idat['fioc']
        else:
            if itype == 'Feature':
                if not status:
                    nfioc = 'f' + idat['fioc'] [1]
                elif status == 'Open':
                    nfioc = 'fo'
                elif status == 'Closed':
                    nfioc = 'fc'
            elif itype == 'Issue':
                if not status:
                    nfioc = 'i' + idat['fioc'] [1]
                elif status == 'Open':
                    nfioc = 'io'
                elif status == 'Closed':
                    nfioc = 'ic'

        item = data.project[pid] ['milestone'] [idat['x']] [idat['y']] \
                [idat['fioc']] [item_id]
        data.project[pid] ['milestone'] [nx] [ny] [nfioc] [item_id] = item
        del data.project[pid] ['milestone'] [idat['x']] [idat['y']] \
                [idat['fioc']] [item_id]
        data.project[pid] ['ri_index'] [item_id] = (new_major, new_minor,
                                                         nfioc)
        self.touchItem(pid, item_id)
        self.updateMilestoneTree(pid)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def closeItem(self, pid, item_id):

        idat = self.getItemData(pid, item_id)
        self.moveItem(pid, item_id, idat['major'], idat['minor'], idat['itype'],
                      'Closed')
        self.touchItem(pid, item_id)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def reopenItem(self, pid, item_id):

        idat = self.getItemData(pid, item_id)
        self.moveItem(pid, item_id, idat['major'], idat['minor'], idat['itype'],
                      'Open')
        self.touchItem(pid, item_id)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def deleteItem(self, pid, item_id):

        idat = self.getItemData(pid, item_id)
        del data.project[pid] ['milestone'] [idat['x']] [idat['y']] \
                [idat['fioc']] [item_id]
        del data.project[pid] ['ri_index'] [item_id]
        self.updateMilestoneTree(pid)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

