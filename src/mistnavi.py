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

    # compute feature / issue count
    for miid in dc.sp.m._(major)._(minor).index.v:

        if dc.sp.m.mi._(miid).mtype.v == 'Feature':
            out.total_features += 1

            if dc.sp.m.mi._(miid).status.v == 'Open':
                out.open_features += 1

        if dc.sp.m.mi._(miid).mtype.v == 'Issue':
            out.total_issues += 1

            if dc.sp.m.mi._(miid).status.v == 'Open':
                out.open_issues += 1

    amajor, aminor = dc.sp.m.active.v

    # compute diamond and delta

    # different major version than active
    if major < amajor:
        out.diamond = '◆'
        out.delta_sign = '-'
        out.delta_major = amajor - major

        inActive = aminor
        inBetween = 0
        for x in range(major+1, amajor):
            inBetween += len(dc.sp.m._(x).index.v)

        inCalc = len(dc.sp.m._(major).index.v) - minor
        if major == 0:
            inCalc += 1

        out.delta_minor = inActive + inBetween + inCalc

    elif major > amajor:
        out.diamond = '◇'
        out.delta_sign = '+'
        out.delta_major = major - amajor

        inActive = len(dc.sp.m._(amajor).index.v) - aminor
        if amajor == 0:
            inActive += 1

        inBetween = 0
        for x in range(amajor+1, major):
            inBetween += len(dc.sp.m._(x).index.v)
        inCalc = minor

        out.delta_minor = inActive + inBetween + inCalc

    # same major verson as active
    else:

        out.delta_major = 0

        if minor < aminor:
            out.diamond = '◆'
            out.delta_sign = '-'
            out.delta_minor = aminor - minor
        elif minor > aminor:
            out.diamond = '◇'
            out.delta_sign = '+'
            out.delta_minor = minor - aminor
        else:
            out.diamond = '◈'
            out.delta_sign = '+'
            out.delta_minor = 0

    # compose label
    out.label = '{}  v{}.{}  {}{}:{}   f:{}/{}  i:{}/{}'.format(
                    out.diamond,
                    major,
                    minor,
                    out.delta_sign,
                    out.delta_major,
                    out.delta_minor,
                    out.total_features - out.open_features,
                    out.total_features,
                    out.total_issues - out.open_issues,
                    out.total_issues)

    return out

@logger('(mistnavi) computeMajorLabelItems(major)', 'major')
def computeMajorLabelItems(major):

    out = LabelComputation()

    minors = dc.sp.m._(major).index.v
    for minor in minors:

        for miid in dc.sp.m._(major)._(minor).index.v:

            if dc.sp.m.mi._(miid).mtype.v == 'Feature':
                out.total_features += 1

                if dc.sp.m.mi._(miid).status.v == 'Open':
                    out.open_features += 1

            if dc.sp.m.mi._(miid).mtype.v == 'Issue':
                out.total_issues += 1

                if dc.sp.m.mi._(miid).status.v == 'Open':
                    out.open_issues += 1

    amajor, aminor = dc.sp.m.active.v

    if major < amajor:
        out.diamond = '◆'
        out.delta_sign = '-'
        out.delta_major = amajor - major

    elif major > amajor:
        out.diamond = '◇'
        out.delta_sign = '+'
        out.delta_major = major - amajor

    else:
        out.diamond = '◈'
        out.delta_sign = '+'
        out.delta_major = 0

    # compose label
    out.label = '{}  v{}  {}{}  f:{}/{}  i:{}/{}'.format(
                    out.diamond,
                    major,
                    out.delta_sign,
                    out.delta_major,
                    out.total_features - out.open_features,
                    out.total_features,
                    out.total_issues - out.open_issues,
                    out.total_issues)

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

    # update only one milestone entry (on milestone item cont / status change)
    @logger('MilestoneButton.updateMajorMilestone(self, major)', 'self', 'major')
    def updateMajorMilestone(self, major):

        pass

    @logger('MilestoneButton.updateMenuTree(self)', 'self')
    def updateMenuTree(self):

        for major in dc.sp.m.index.v:

            loop_major_menu = QMenu(self.root_menu)
            loop_major_menu.setTitle(computeMajorLabelItems(major).label)
            self.root_menu.addMenu(loop_major_menu)
            dc.ui.roadmap.menu._(major).v = loop_major_menu

            for minor in dc.sp.m._(major).index.v:

                action = QAction(loop_major_menu)
                action.setText(computeMinorLabelItems(major, minor).label)
                loop_major_menu.addAction(action)

    @logger('MilestoneButton.onSelectionChanged(self)', 'self')
    def onSelectionChanged(self):

        smajor, sminor = dc.sp.m.selected.v
        self.setText(computeMinorLabelItems(smajor, sminor).label)

        self.selectionChanged.emit(self.text())

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


