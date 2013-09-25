# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos, seth.kriticos+nelia1@gmail.com
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Utility functions that don't require datacore. Datacore is using the log
# functions and would cause an infinite import recursion if used in this file.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time
import datetime
import PySide
import sys

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def log(msg):
    if '-debug' in sys.argv:
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

@logger('convert(item)', 'item')
def convert(item):

    if isinstance(item, int):
        return datetime.datetime.fromtimestamp(item).isoformat()

    if item == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
        return PySide.QtCore.Qt.SortOrder.DescendingOrder
    if item == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
        return PySide.QtCore.Qt.SortOrder.AscendingOrder
    raise Exception('convert called with invalid item type or value')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

