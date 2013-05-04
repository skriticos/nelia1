# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, pickle, gzip
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc = _dcNode()
# x = internal, c = config, r = run, s = store (document)
dc.x, dc.c, dc.r, dc.s
dc.x.changed.v = False
dc.x.storepath.v = None
dc.x.appname.v = __APPNAME__
dc.c.lastpath.v = None
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
    path = os.path.join(os.path.expanduser('~'),
        '.config', dc.x.appname.v, '{}.config'.format(dc.x.appname.v))
    pdat = pickle.dumps(dc.c, 3)
    cdat = gzip.compress(pdat)
    with open(path, 'w') as f: f.write(cdat)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def dcloadconfig():
    path = os.path.join(os.path.expanduser('~'),
        '.config', dc.x.appname.v, '{}.config'.format(dc.x.appname.v))
    if not os.path.exists(path): return
    with open(path, 'r') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.c = pickle.loads(pdat)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dcdump(node=None, path=''):
    if not node: node = dc
    if node.v: print('dc.' + path + '.v = ', node.v)
    for x in node.__dict__.keys():
        if isinstance(node.__dict__[x], _dcNode):
            _dcdump(node=node.__dict__[x], path=path + bool(path)*'.' + x)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

