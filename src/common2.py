# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common methods that require datacore.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from PySide.QtCore import *
from PySide.QtGui import *

from datacore import dc
from common import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# save / load layout of table
#
# Tables use the same datacore layout in all three gui control modules:
#
#   dc.c._(module).*, dc.x._(module).*
#
# These methods unify header with and sort order configuration saving and
# loading.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('saveLayout(module)', 'module')
def saveLayout(module):

    dc.c._(module).header.width.v = list()
    for i in range(dc.x._(module).model.v.columnCount()):
        dc.c._(module).header.width.v.append(dc.x._(module).view.v.columnWidth(i))

    sort  = dc.x._(module).horizontal_header.v.sortIndicatorSection()
    order = dc.x._(module).horizontal_header.v.sortIndicatorOrder().__repr__()
    dc.c._(module).sort.column.v = sort
    dc.c._(module).sort.order.v  = order

@logger('loadLayout(module)', 'module')
def loadLayout(module):

    for i, v in enumerate(dc.c._(module).header.width.v):
        dc.x._(module).view.v.setColumnWidth(i, v)

    if dc.c._(module).sort.column.v:
        dc.x._(module).horizontal_header.v.setSortIndicator(
            dc.c._(module).sort.column.v, convert(dc.c._(module).sort.order.v))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# set table value
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('setTableValue(module, col, value)', 'module', 'col', 'value')
def setTableValue(module, col, value):

    row = dc.x._(module).row.v

    if row != None and row > -1:
        dc.x._(module).model.v.setItem(row, col, QStandardItem(value))
    else:
        # Famous last words: this should never happen
        log('NO ROW SELECTED')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Applies states to widgets.
#
#   applyStates({'myButton': {'enabled': True, 'visible': True}, dc.ui.myWidget.v)
#
# This example applies enabled and visible attribute on the myButton button in
# the myWidget widget.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('applyStates(states, widget)', 'states', 'widget')
def applyStates(states, widget):

    autoprev = dc.auto.v
    dc.auto.v = True

    for control, state in states.items():

        pd = widget.__dict__
        if 'enabled' in state:
            pd[control].setEnabled(state['enabled'])
        if 'visible' in state:
            pd[control].setVisible(state['visible'])
        if 'margins' in state:
            pd[control].setContentsMargins(*state['margins'])
        if 'text' in state:
            pd[control].setText(state['text'])
        if 'clear' in state:
            pd[control].clear()
        if 'index' in state:
            pd[control].setCurrentIndex(state['index'])
        if 'value' in state:
            pd[control].setValue(state['value'])
        if 'focused' in state:
            pd[control].setFocus()
        if 'isreadonly' in state:
            pd[control].setReadOnly(state['isreadonly'])
        if 'iswritable' in state:
            pd[control].setReadOnly(not state['iswritable'])
    dc.auto.v = autoprev

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

