# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from datacore import *
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# called when new project is created. creates an new intial milestone tree for
# the currently selected project (dc.sp)
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
    dc.sp.m._0.nextminor.v = 1
    dc.sp.m._1._0.index.v = set()   # index miids in milestone
    dc.sp.m._1._0.description.v  = ''    # milestone description
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

