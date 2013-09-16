# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from datacore import *
from common import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# called when new project is created. creates an new intial milestone tree for
# the currently selected project (dc.sp)
@logger('(mistctrl) mistctrl_new_tree()')
def mistctrl_new_tree():

    # milestone items
    dc.sp.m.mi.nextid.v   = 1       # next new milestone id
    dc.sp.m.mi.index.v    = {}      # miid → (major, minor) index
    dc.sp.m.mi.selected.v = None    # selected milestone item (int)

    # milestones general
    dc.sp.m.active.v      = (0, 1)  # active milestone
    dc.sp.m.selected.v    = (0, 1)  # selected milestone
    dc.sp.m.index.v       = {0, 1}  # index of major milestones
    dc.sp.m.nextmajor.v   = 2       # next major milestone

    # v0.1
    dc.sp.m._0.index.v    = {1}     # index of minor milestones
    dc.sp.m._0.nextminor.v = 2
    dc.sp.m._0._1.index.v = set()   # index miids in milestone
    dc.sp.m._0._1.detail.v  = ''    # milestone description

    # v1.0
    dc.sp.m._1.index.v    = {0}     # index of minor milestones
    dc.sp.m._1.nextminor.v = 1
    dc.sp.m._1._0.index.v = set()   # index miids in milestone
    dc.sp.m._1._0.description.v  = ''    # milestone description

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('(mistctrl) calibrateRoadmapMi()')
def calibrateRoadmapMi():
    """
        This is called when milestone items are added or removed.
        It calibrates the roadmap tree and ensures that no two empty milestones
        follow each other and the last minor milestone is always empty.
    """

    major, minor = dc.sp.m.selected.v
    nextminor = dc.sp.m._(major).nextminor.v

    if dc.sp.m._(major)._(nextminor - 1).index.v:

        dc.sp.m._(major).index.v |= {nextminor}
        dc.sp.m._(major).nextminor.v += 1

        dc.sp.m._(major)._(nextminor).index.v = set()
        dc.sp.m._(major)._(nextminor).description.v = ''

    elif not dc.sp.m._(major)._(nextminor - 2).index.v:

        dc.sp.m._(major).index.v -= {nextminor - 1}
        dc.sp.m._(major).nextminor.v -= 1

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('(mistctrl.calibrateMinorMsClosed()')
def calibrateMinorMsClosed():

    """
        Invoked when a minor milestone itme is closed. It calibrates the
        roadmap tree. This is simple, we just increment the minor counter.
    """

    smajor, sminor = dc.sp.m.selected.v
    amajor, aminor = dc.sp.m.active.v

    if dc.sp.m.selected.v != dc.sp.m.active.v:

        raise Exception('selected, active missmatch on minor milestone'
                        'calibration')

    dc.sp.m.active.v = (amajor, aminor + 1)
    dc.sp.m.selected.v = (amajor, aminor + 1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('(mistctrl.calibrateMajorMsClosed()')
def calibrateMajorMsClosed():

    """
        Invoked when a major milestone itme is closed. It calibrates the
        roadmap tree.
    """

    smajor, sminor = dc.sp.m.selected.v
    amajor, aminor = dc.sp.m.active.v

    if dc.sp.m.selected.v != dc.sp.m.active.v:

        raise Exception('selected, active missmatch on minor milestone'
                        'calibration')

    # remove next minor in active branch as we close the major branch
    nextminor = sminor + 1
    dc.sp.m._(smajor).index.v -= {nextminor}
    del dc.sp.m._(smajor).__dict__['_{}'.format(nextminor)]

    # set the milestone status
    dc.sp.m.active.v = (amajor + 1, 0)
    dc.sp.m.selected.v = (amajor + 1, 0)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

