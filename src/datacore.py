# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The application uses a somewhat eccentric data storage and communication
# mechanism: the datacore. The datacore basically contains all configuration,
# document data and most of the runtime data including references to all modules
# and utilies, state data and everything else relating to data.
#
# The datacore is basically a big, self expanding tree. The root node is
# imported at the top of every sourcefile (from datacore import dc).
#
# Creating new nodes is done by simply refering to the:
#
#       dc.foo.bar.v = 'baz'
#
# This creates subnodes foo and for and assigns a value (always stored in .v).
# _dcdump is a debug utility that is used to print a listing of a datacore
# branch.
#
#       _dcdump(dc.foo.bar, 'foo.bar')
#
# This will dump all data that is below this datacore node.
#
# Document and configuration serialization is also handled by datacore.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import pickle
import gzip

from common import log, logger

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class _dcNode:

    def __init__(self, name):
        self.v = None
        self._name = name

    # if we try to access an previously non-existent subkey, we'll create this
    # key automatically with this method
    def __getattr__(self, key):
        name = '{}.{}'.format(self._name, key)
        self.__dict__[key] = _dcNode(name)
        return self.__dict__[key]

    # set a key. this method is used to capture assignment info for
    # logging/debugging
    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if '_name' in self.__dict__ and key != '_name':
            log('DAT  {}.{} = {}'.format(self.__dict__['_name'], key, value))

    # a number is not a valid subkey, so we prefix it with an underscore
    # e.g. x._(10).v = 'foo'. Good for enumerated data.
    def _(self, key):
        k = key
        if isinstance(key, int):
            k = '_' + str(key)
        name = '{}.{}'.format(self._name, k)
        if k not in self.__dict__:
            self.__dict__[k] = _dcNode(name)
        return self.__dict__[k]

    # used to save documents / configuration
    def __serialize__(self, data={}):
        data['_dcNode'] = {}
        for key, value in self.__dict__.items():
            if isinstance(value, _dcNode):
                data['_dcNode'][key] = {}
                value.__serialize__(data['_dcNode'][key])
            else:
                data[key] = value
        if not data['_dcNode']: del data['_dcNode']
        return data

    def __deserialize__(self, data):
        for key, value in data.items():
            if key == '_dcNode':
                for key in value:
                    name = '{}.{}'.format(self._name, key)
                    n = self.__dict__[key] = _dcNode(name)
                    n.__deserialize__(value[key])
            else:
                self.__dict__[key] = value

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# initialize initial datacore
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

dc = _dcNode('dc')
dc.x, dc.s, dc.m, dc.states, dc.ui, dc.spid, dc.sp

dc.c.lastpath.v = None
dc.x.appname.v = 'nelia1'
dc.x.home.v = os.path.expanduser('~')
dc.x.config.basepath.v = os.path.join(dc.x.home.v, '.config', dc.x.appname.v)
dc.x.config.filepath.v = os.path.join(dc.x.config.basepath.v, '{}.config'.format(dc.x.appname.v))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# document and configuration save / load
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@logger('dcsave(path=None)')
def dcsave(path=None):
    if not path and not dc.x.path.v:
        raise ValueError('Storepath not defined')
    if path: dc.x.path.v = path
    pdat = pickle.dumps(dc.s.__serialize__(), 3)
    cdat = gzip.compress(pdat)
    with open(dc.x.path.v, 'wb') as f: f.write(cdat)
    dc.c.lastpath.v = dc.x.path.v
    dc.x.changed.v = False

@logger('dcload(path)', 'path')
def dcload(path):
    with open(path, 'rb') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.s.__deserialize__(pickle.loads(pdat))
    dc.x.path.v = path
    dc.x.changed.v = False

@logger('dcsaveconfig()')
def dcsaveconfig():
    os.makedirs(dc.x.config.basepath.v, exist_ok=True)
    pdat = pickle.dumps(dc.c.__serialize__(), 3)
    cdat = gzip.compress(pdat)
    with open(dc.x.config.filepath.v, 'wb') as f: f.write(cdat)
    return True

@logger('dcloadconfig()')
def dcloadconfig():
    if not os.path.exists(dc.x.config.filepath.v): return
    with open(dc.x.config.filepath.v, 'rb') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.c.__deserialize__(pickle.loads(pdat))
    dc.x.config.loaded.v = True

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _dcdump(node=None, path=''):
    if not node: node = dc
    if node.v is not None:
        if node.v == '':
            print('dc.' + path + '.v =  \'\'')
        else:
            print('dc.' + path + '.v = ', node.v)
    for x in node.__dict__.keys():
        if isinstance(node.__dict__[x], _dcNode):
            try:
                _dcdump(node=node.__dict__[x], path=path + bool(path)*'.' + x)
            except:
                raise Exception('datacore inconsistency found at: {}, {}'.format(path, x))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

