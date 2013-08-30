# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This file contains the milestone navigation summary view and selection button,
# mistnavi for short. It provides a button that shows the open and closed
# features and issuses of the currently selected milestone and the status of the
# selected milestone (closed, active, future). It provides a two level dropdown
# menu to enable a milestone selection change to any other milestone of the
# project.
#
# We are using a shadow tree that is updated on milestone changes to avoid
# lengthly re-calculation.
#
# dc.sp.m.shadow._(major)._(minor).v = '♦  vM.N  f:A/B  i:C/D'
#
# core data of interest for this module
# dc.sp.m.mi._(miid).*.v .. [name, status, mtype]
# dc.sp.m.index.v
# dc.sp.m._(major).index.v
# dc.sp.m._(major)._(minor).index.v
# dc.sp.m.active.v
# dc.sp.m.selected.v
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from PySide.QtCore import *
from PySide.QtGui import *

from datacore import *
from common import *
from common2 import *

import mistctrl                       # milestone control module for new project

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                   UTILITY
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class util: pass

class LabelComputation:

    def __init__(self):

        # label for minors is like '◇  v0.0  +0:0  f:0/0  i:0/0'
        # label for major  is like '◇  v0.x  +0  f:0/0  i:0/0'
        self.label = ''
        self.diamond = '◇ ◈ ◆'
        self.open_features = 0
        self.total_features = 0
        self.open_issues = 0
        self.total_issues = 0
        self.delta_major = 0
        self.delta_minor = 0
        self.delta_sign = '+'

@logger('(mistnavi) computeMinorLabelItems(major, minor)', 'major', 'minor')
def computeMinorLabelItems(major, minor):

    out = LabelComputation()

    return out

@logger('(mistnavi) computeMajorLabelItems(major)', 'major')
def computeMajorLabelItems(major):

    out = LabelComputation()
    out.delta_minor = 'x'

    return out

util.LabelComputation = LabelComputation
util.computeMinorLabelItems = computeMinorLabelItems
util.computeMajorLabelItems = computeMajorLabelItems

dc.m.mistnavi.util.v = util

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                 CORE CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class MilestoneButton(QPushButton):

    selectionChanged = Signal(str)

    @logger('MilestoneButton.__init__(self, parent=None)', 'self')
    def __init__(self, parent=None, smajor=0, sminor=1):

        super().__init__(parent)

        self.root_menu = QMenu(self)
        self.setMenu(self.root_menu)

        self.updateMenuTree()

    # update only one milestone entry (on milestone item cont / status change)
    @logger('MilestoneButton.updateMajorMilestone(self, major)', 'self', 'major')
    def updateMajorMilestone(self, major):

        pass

    @logger('MilestoneButton.updateMenuTree(self)', 'self')
    def updateMenuTree(self):

        pass

    @logger('MilestoneButton.onSelectionChanged(self)', 'self')
    def onSelectionChanged(self):

        # TODO: fill in signal string
        self.selectionChanged.emit('')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


