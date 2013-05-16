# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from PySide.QtCore import *
from PySide.QtGui import *
import time
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def updateMilestoneTree():
    for imajor in reversed(list(dc.sp.m.idx.v)):
        # major branch receaves first item
        if imajor > 0 and imajor+1 not in dc.sp.m.idx.v \
                      and len(dc.sp.m._(imajor)._(0).idx.v):
            print('... updateMilestoneTree: adding major {}.0 and minor {}.{}'.format(imajor+1, imajor, 1))
            # add imajor+1.0, imajor.1
            dc.sp.m.idx.v.add(imajor+1)
            dc.sp.m._(imajor+1).idx.v = {0}
            dc.sp.m._(imajor+1)._(0).description.v = ''
            dc.sp.m._(imajor+1)._(0).idx.v = set()
            dc.sp.m._(imajor).idx.v.add(1)
            dc.sp.m._(imajor)._(1).description.v = ''
            dc.sp.m._(imajor)._(1).idx.v = set()
            continue
        # major branch looses last item
        elif imajor > 1 and not len(dc.sp.m._(imajor-1)._(0).idx.v):
            print('... updateMilestoneTree: removing major', imajor)
            del dc.sp.m.__dict__['_{}'.format(imajor)]
            dc.sp.m.idx.v.remove(imajor)
            continue
        lminor = max(dc.sp.m._(imajor).idx.v)
        print('... updateMilestoneTree: imajor {}, lminor {}'.format(imajor, lminor))
        if imajor is 0 and lminor is 1 and not dc.sp.m._(0)._(1).idx.v:
            break
        # last minor branch receaves first item
        if len(dc.sp.m._(imajor)._(lminor).idx.v):
            print('... updateMilestoneTree: adding minor milestone')
            dc.sp.m._(imajor).idx.v.add(lminor+1)
            dc.sp.m._(imajor)._(lminor+1).description.v = ''
            dc.sp.m._(imajor)._(lminor+1).idx.v = set()
        # previous to last minor branch looses last item
        elif lminor and not len(dc.sp.m._(imajor)._(lminor-1).idx.v):
            print('... updateMilestoneTree: removing minor {}.{}'.format(imajor, lminor))
            dc.sp.m._(imajor).idx.v.remove(lminor)
            del dc.sp.m._(imajor).__dict__['_{}'.format(lminor)]
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def addMI(major, minor, itype, category,
          name, priority, description, status='Open'):
    # milestone item id
    miid = dc.sp.nextmiid.v
    dc.sp.nextmiid.v += 1
    # milestone item location
    dc.sp.midx.v[miid] = major, minor
    # milestone item attributes
    dc.sp.mi._(miid).name.v = name
    dc.sp.mi._(miid).description.v = description
    dc.sp.mi._(miid).priority.v = priority
    dc.sp.mi._(miid).category.v = category
    dc.sp.mi._(miid).itype.v = itype
    dc.sp.mi._(miid).status.v = status
    t = int(time.time())
    dc.sp.mi._(miid).created.v = t
    dc.sp.mi._(miid).modified.v = t
    # milestone item reference in tree
    dc.sp.m._(major)._(minor).idx.v.add(miid)
    updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def editMI(major, minor, miid, itype, category, name, priority, description):
    if (major, minor) != dc.sp.midx.v[miid]:
        old_major, old_minor = dc.sp.midx.v[miid]
        dc.sp.m._(old_major)._(old_minor).idx.v.remove(miid)
        dc.sp.m._(major)._(minor).idx.v.add(miid)
        dc.sp.midx.v[miid] = major, minor
    dc.sp.mi._(miid).itype.v = itype
    dc.sp.mi._(miid).name.v  = name
    dc.sp.mi._(miid).category.v = category
    dc.sp.mi._(miid).priority.v = priority
    dc.sp.mi._(miid).description.v = description
    dc.sp.mi._(miid).changed.v = int(time.time())
    updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def closeMI(miid):
    dc.sp.mi._(miid).status.v = 'Closed'
    dc.sp.mi._(miid).changed.v = int(time.time())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def reopenMI(miid):
    dc.sp.mi._(miid).status.v = 'Open'
    dc.sp.mi._(miid).changed.v = int(time.time())
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def deleteMI(miid):
    del dc.sp.mi.__dict__['_{}'.format(miid)]
    major, minor = dc.sp.midx.v[miid]
    del dc.sp.midx.v[miid]
    dc.sp.m._(major)._(minor).idx.v.remove(miid)
    updateMilestoneTree()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == '__main__':
    # initial data
    dc.sp.nextmiid.v    = 1
    dc.sp.curr.major.v  = 0
    dc.sp.curr.minor.v  = 0
    dc.sp.midx.v = {}
    dc.sp.m._(0)._(1).description.v = ''
    dc.sp.m._(0)._(1).idx.v = set()
    dc.sp.m._(1)._(0).description.v = ''
    dc.sp.m._(1)._(0).idx.v = set()
    dc.sp.m.idx.v = {0, 1}
    dc.sp.m._(0).idx.v = {1}
    dc.sp.m._(1).idx.v = {0}

    print('\initial data')
    from datacore import _dcdump
    _dcdump(dc.sp)
    print('\ndry-run updateMilestoneTree (should not change anything)')
    updateMilestoneTree()
    assert (dc.sp.m.idx.v == {0, 1})
    assert (dc.sp.m._(0).idx.v == {1})
    assert (dc.sp.m._(1).idx.v == {0})
    _dcdump(dc.sp)

    # add milestone item to 0.1
    # check item attributes
    # check milestone item index
    # check milestone update (0.1, 0.2, 1.0)
    # def addMI(major, minor, itype, category,
    #          name, priority, description, status='Open'):
    print('\nadding feature to 0.1')
    print('this should create milestone 0.2')
    print('dc.sp.m._0._2.*')
    print("run addMI(0, 1, 'type', 'cat', 'name', 0, 'desc')")
    addMI(0, 1, 'type', 'cat', 'name', 0, 'desc')
    _dcdump(dc.sp)
    assert(dc.sp.mi._(1).name.v == 'name')
    assert(dc.sp.midx.v[1] == (0, 1))
    assert(dc.sp.m._(0).idx.v == {1, 2})
    assert(dc.sp.m._(1).idx.v == {0})


