from PySide.QtCore import *
from PySide.QtGui import *
import time

class NxMilestone:

    def __init__(self, parent, data):

        self.parent = parent
        self.data = data

    def versionToIndex(self, major, minor):

        """
            Helper.
            Shorthand to get array address from milestone version number.
            This has to be done, as the major version 0 branch starts with
            minor version 1, and all others with 0.
        """

        if major > 0:
            return major, minor
        else:
            return major, minor - 1

    def indexToVersion(self, x, y):

        if major > 0:
            return x, y
        else:
            return x, y + 1

    def getItemData(self, pid, itemId):

        p = self.data.project[pid]
        ma, mi, fioc = p['ri_index'][item_id]
        x, y = self.versionToIndex(ma, mi)
        item = p['milestone'][x][y][fioc]

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

    def getAttribute(self, pid, item_id, attr_name):

        idat = self.getItemData(pid, itme_id)
        return idat[attr_name]

    def setAttibute(self, pid, itme_id, attr_name, value):

        idat = self.getItemData(pid, itme_id)
        self.data.project[pid]['milestone'][idat['x']][idat['y']][idat['fioc']][item_id][attr_name] = value

    def touchItem(self, pid, item_id):

        self.setAttibute(self, pid, item_id, 'modified', int(time.time()))

    def addItem(self, pid, major, minor, itype, icat, name, priority, description, status='Open'):

        """
            p: project id
            major: major version
            minor: minor version
            itype: item type 'Feature'|'Issue'
            icat: item category 'Functional'|'Security'|'Convenience'
            name: name
            priority: 'Low'|'Medium'|'High'
            description: free form plain text
            status: item status 'Open'|'Closed'
        """

        item_id = self.data.project[pid]['meta']['last_roadmap_item'] + 1

        new_item = {
            'name': name,
            'icat': icat,
            'priority': priority,
            'description': description,
            'status': status,
            'created': int(time.time()),
        }

        x, y = self.versionToIndex(major, minor)
        if itype == 'Feature':
            fioc = 'fo'
        elif itype == 'Issue':
            fioc = 'io'

        self.data.project[pid]['milestone'][x][y][fioc] = new_item
        self.data.project[pid]['ri_index'][item_id] = (major, minor, fioc)

        self.touchItem(pid, item_id)
        self.data.project[pid]['meta']['last_roadmap_item'] += 1

    def editItem(self, pid, major, minor, item_id, itype, icat, name, priority, description):

        idat = self.getItemData(pid, item_id)
        for k, v in (
            ('icat', icat),
            ('name', name),
            ('priority', priority),
            ('description', description)
        ):
            self.setAttibute(pid, item_id, k, v)

        if itype != idat['status'] or major != idat['major'] or minor != idat['minor']:
            self.moveItem(pid, item_id, major, minor, itype, idat['status'])

        self.touchItem(pid, item_id)

    def moveItem(self, pid, item_id, new_major, new_minor, itype=None, status=None):

        idat = self.getItemData(pid, item_id)
        nx, ny = self.versionToIndex(new_major, new_minor)

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

        item = self.data.project[pid]['milestone'][idat['x']][idat['y']][idat['fioc']]
        self.data.project[pid]['milestone'][nx][ny][nfioc][item_id] = item
        del self.data.project[pid]['milestone'][idat['x']][idat['y']][idat['fioc']]
        self.data.project[pid]['ri_index'][item_id] = (nx, ny, nfioc)
        self.touchItem(pid, item_id)

    def closeItem(self, pid, item_id):

        idat = self.getItemData(pid, item_id)
        self.moveItem(pid, item_id, idat['major'], idat['minor'], idat['itype'], 'Closed')
        self.touchItem(pid, item_id)

    def deleteItem(self, pid, item_id):

        idat = self.getItemData(pid, item_id)
        del self.data.project[pid]['milestone'][idat['x']][idat['y']][idat['fioc']][item_id]
        del self.data.project[pid]['ri_index'][item_id]

