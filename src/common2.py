# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common methods that require datacore instance.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from PySide.QtCore import *
from PySide.QtGui import *

from datacore import dc
from common import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# SAVE / LOAD LAYOUT OF TABLE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# we assume that the GUI module widget tables have the same naming convention in
# datacore.

@logger('saveLayout(module)', 'module')
def saveLayout(module):

    # save header widths
    dc.c._(module).header.width.v = list()
    for i in range(dc.x._(module).model.v.columnCount()):
        dc.c._(module).header.width.v.append(dc.x._(module).view.v.columnWidth(i))

    # save sort column / order
    sort  = dc.x._(module).horizontal_header.v.sortIndicatorSection()
    order = dc.x._(module).horizontal_header.v.sortIndicatorOrder().__repr__()
    dc.c._(module).sort.column.v = sort
    dc.c._(module).sort.order.v  = order

@logger('loadLayout(module)', 'module')
def loadLayout(module):

    # load header widths
    for i, v in enumerate(dc.c._(module).header.width.v):
        dc.x._(module).view.v.setColumnWidth(i, v)

    # load sorting
    if dc.c._(module).sort.column.v:
        dc.x._(module).horizontal_header.v.setSortIndicator(
            dc.c._(module).sort.column.v, convert(dc.c._(module).sort.order.v))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TABLE VALUE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# This sets a cell value in the currently selected table item.
# Don't feed this method anything 'non-string' as value, or it will throw
# segmentation faults at you!

@logger('setTableValue(module, col, value)', 'module', 'col', 'value')
def setTableValue(module, col, value):
    row = dc.x._(module).selection_model.v.currentIndex().row()
    if row > -1:
        dc.x._(module).model.v.setItem(row, col, QStandardItem(value))
    else:
        # Famous last words: this should never happen
        log('NO ROW SELECTED')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

