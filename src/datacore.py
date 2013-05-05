# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, pickle, gzip, datetime, PySide
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
__APPNAME__ = 'nelia1' # required for config save
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class _dcNode:
    def __init__(self):
        self.v = None
    def __getattr__(self, key):
        self.__dict__[key] = _dcNode()
        return self.__dict__[key]
    def _(self, key):
        k = key
        if isinstance(key, int): k = '_' + str(key)
        if k not in self.__dict__: self.__dict__[k] = _dcNode()
        return self.__dict__[k]
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
                    n = self.__dict__[key] = _dcNode()
                    n.__deserialize__(value[key])
            else:
                self.__dict__[key] = value
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc = _dcNode()
# x = internal, c = config, r = run, s = store (document)
dc.x, dc.c, dc.r, dc.s
dc.x.path.v = None
dc.x.appname.v = __APPNAME__
dc.c.lastpath.v = None
# config path related stuff
dc.x.home.v = os.path.expanduser('~')
dc.x.config.basepath.v = os.path.join(dc.x.home.v, '.config', dc.x.appname.v)
dc.x.config.filepath.v \
    = os.path.join(dc.x.config.basepath.v, '{}.config'.format(dc.x.appname.v))
# document path stuff
dc.x.extension.v = '.nelia1'
dc.x.default.path.v = os.path.expanduser('~/Documents')
# default document values
dc.s.nextpid.v = 1
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dcsave(path=None):
    if not path and not dc.x.storepath.v:
        raise ValueError('Storepath not defined')
    if path: dc.x.storepath.v = path
    pdat = pickle.dumps(dc.s, 3)
    cdat = gzip.compress(pdat)
    with open(dc.x.storepath.v, 'w') as f: f.write(cdat)
    dc.x.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dcload(path):
    with open(path, 'r') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.s = pickle.loads(pdat)
    dc.x.storepath.v = path
    dc.x.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dcsaveconfig():
    os.makedirs(dc.x.config.basepath.v, exist_ok=True)
    pdat = pickle.dumps(dc.c.__serialize__(), 3)
    cdat = gzip.compress(pdat)
    with open(dc.x.config.filepath.v, 'wb') as f: f.write(cdat)
    return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dcloadconfig():
    if not os.path.exists(dc.x.config.filepath.v): return
    with open(dc.x.config.filepath.v, 'rb') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.c.__deserialize__(pickle.loads(pdat))
    dc.x.config.loaded.v = True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dcdump(node=None, path=''):
    if not node: node = dc
    if node.v: print('dc.' + path + '.v = ', node.v)
    for x in node.__dict__.keys():
        if isinstance(node.__dict__[x], _dcNode):
            _dcdump(node=node.__dict__[x], path=path + bool(path)*'.' + x)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def convert(item):
    # convert timestamps (int)
    if isinstance(item, int):
        return datetime.datetime.fromtimestamp(item).isoformat()
    # we can't pickle PySide objects :(
    if item == 'PySide.QtCore.Qt.SortOrder.DescendingOrder':
        return PySide.QtCore.Qt.SortOrder.DescendingOrder
    if item == 'PySide.QtCore.Qt.SortOrder.AscendingOrder':
        return PySide.QtCore.Qt.SortOrder.AscendingOrder
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

