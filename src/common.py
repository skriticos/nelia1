# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Common utility functions that do not reqire datacore. Datacore imporrts this,
# so not importing datacore here is a hard requirement for the application to
# work.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time
import datetime
import PySide

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# logging (debugging). dumps all calls during runtime, including data assignment
# in datacore. set the logger as decorator for all methods

def log(msg):
    msg = '{:.4f}: {}'.format(time.time(), msg)
    print(msg)

def logMarker():
    log('********** MARKER **********')

def logger(name, *argnames):
    def wrap(func):
        def wrapped(*args, **kwargs):
            arglist = ''
            for i in range(len(argnames)):
                arglist += '{}:{}, '.format(argnames[i], args[i])
            if len(arglist):
                arglist = arglist[:-2]
            arglist = '({})'.format(arglist)
            msg = 'CALL {} with args{} and kwargs {}'.format(
                  name, arglist, kwargs)
            log(msg)
            retval = func(*args, **kwargs)
            if retval:
                msg = 'RET  {} -> ({})'.format(name, retval)
                log(msg)
            return retval
        return wrapped
    return wrap

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Applies a suite of states to widgets.
#
#   enabled: en/disable widget, bool
#   visible: show/hide wiget, bool
#   margins: set margins (n,n,n,n)
#   text: set text (for input boxes and labels)
#   clear: clear widget
#   index: set index for comboboxes
#   value: set value for spinboxes

@logger('applyStates(states, widget)', 'states', 'widget')
def applyStates(states, widget):

    # loop through controls (widgets)
    for control, state in states.items():

        # loop through state attributes
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('convert(item)', 'item')
def convert(item):
    # convert timestamps (int)
    if isinstance(item, int):
        return datetime.datetime.fromtimestamp(item).isoformat()
    # we can't pickle PySide objects :(
    if item == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
        return PySide.QtCore.Qt.SortOrder.DescendingOrder
    if item == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
        return PySide.QtCore.Qt.SortOrder.AscendingOrder
    raise Exception('convert called with invalid item type or value')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

