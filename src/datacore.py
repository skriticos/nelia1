# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# DataCore unifies all data used through the application. Think of it as a big
# dictionary with all non-local data (documents, configuration, runtime, gui,
# etc.). You access values with dc.key.subkey.v. You create new subkeys just by
# refering to them the first time. Keys in the dc.s.. branch are stored into a
# document file. Keys within the dc.c branch are stored into the configuration
# file. All other keys are runtime dc.ui -> ui, dc.m -> modules, dc.x -> general
# runtime, dc.<any other key> -> runtime.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import pickle
import gzip

from common import log, logger

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This is the heart of the DataCore. It's a class that recursively creates
# sub-instances (dc being the root instance). So, if you say dc.x.y.v = 10, then
# dc will create a member x which will create a member y which will assign 10 to
# it's v key. v is always the value key. To get the value back, you just say
# dc.x.y.v .

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
# initialize initial datacore data

# dc is the rootnode to access the datacore though the application.
# it's imported with from datacore import dc and shares the same data through
# the modules (no more annoying passing data all around. just address datacore).
dc = _dcNode('dc')
dc.x, dc.c, dc.r, dc.s

# some initial values for datacore (application specific)
dc.x.path.v = None
dc.x.appname.v = 'nelia1'
dc.c.lastpath.v = None
dc.x.home.v = os.path.expanduser('~')
dc.x.config.basepath.v = os.path.join(dc.x.home.v, '.config', dc.x.appname.v)
dc.x.config.filepath.v = os.path.join(dc.x.config.basepath.v, '{}.config'.format(dc.x.appname.v))
dc.x.extension.v = '.nelia1'
dc.x.default.path.v = os.path.expanduser('~/Documents')
dc.s.nextpid.v = 1
dc.s.index.pid.v = set()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# The following four methods save/load an applicaiton document or the
# configuration.

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
# This method can be used for debugging. It shows all or part of the datacore
# tree (hides None data nodes).

def _dcdump(node=None, path=''):
    if not node: node = dc
    if node.v is not None:
        if node.v == '':
            print('dc.' + path + '.v =  \'\'')
        else:
            print('dc.' + path + '.v = ', node.v)
    for x in node.__dict__.keys():
        if isinstance(node.__dict__[x], _dcNode):
            _dcdump(node=node.__dict__[x], path=path + bool(path)*'.' + x)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

