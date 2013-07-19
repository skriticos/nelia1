# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import os, pickle, gzip, datetime, PySide, time
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
__APPNAME__ = 'nelia1' # required for config save
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def log(msg):
    msg = '{:.4f}: {}'.format(time.time(), msg)
    print(msg)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
class _dcNode:
    def __init__(self, name):
        self.v = None
        self._name = name
    def __getattr__(self, key):
        name = '{}.{}'.format(self._name, key)
        self.__dict__[key] = _dcNode(name)
        return self.__dict__[key]
    def __setattr__(self, key, value):
        self.__dict__[key] = value
        if 'name' in self.__dict__ and key != 'name':
            log('DAT  {}.{} = {}'.format(self.__dict__['name'], key, value))
    def _(self, key):
        k = key
        if isinstance(key, int):
            k = '_' + str(key)
        name = '{}.{}'.format(self._name, k)
        if k not in self.__dict__:
            self.__dict__[k] = _dcNode(name)
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
                    name = '{}.{}'.format(self._name, key)
                    n = self.__dict__[key] = _dcNode(name)
                    n.__deserialize__(value[key])
            else:
                self.__dict__[key] = value
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
dc = _dcNode('dc')
# x = internal, c = config, r = run, s = store (document)
dc.x, dc.c, dc.r, dc.s
dc.x.path.v = None
dc.x.appname.v = __APPNAME__
dc.c.lastpath.v = None
dc.x.home.v = os.path.expanduser('~')
dc.x.config.basepath.v = os.path.join(dc.x.home.v, '.config', dc.x.appname.v)
fp = os.path.join(dc.x.config.basepath.v, '{}.config'.format(dc.x.appname.v))
dc.x.config.filepath.v = fp
dc.x.extension.v = '.nelia1'
dc.x.default.path.v = os.path.expanduser('~/Documents')
dc.s.nextpid.v = 1
dc.s.idx.pid.v = set()
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@logger('dcload(path)', 'path')
def dcload(path):
    with open(path, 'rb') as f: cdat = f.read()
    pdat = gzip.decompress(cdat)
    dc.s.__deserialize__(pickle.loads(pdat))
    dc.x.path.v = path
    dc.x.changed.v = False
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@logger('dcsaveconfig()')
def dcsaveconfig():
    os.makedirs(dc.x.config.basepath.v, exist_ok=True)
    pdat = pickle.dumps(dc.c.__serialize__(), 3)
    cdat = gzip.compress(pdat)
    with open(dc.x.config.filepath.v, 'wb') as f: f.write(cdat)
    return True
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
            _dcdump(node=node.__dict__[x], path=path + bool(path)*'.' + x)
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

