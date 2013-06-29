# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# (c) 2013, Sebastian Bartos <seth.kriticos+nelia1@gmail.com>
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This is a very stripped down version of the datacore. As we are doing runtime
# test only, we removed all the path/save/load/config stuff.
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
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def _dcdump(node=None, path='', output=''):
    if not node: node = dc
    if node.v is not None:
        if node.v == '':
            output += str('dc.' + path + '.v =  \'\'\n')
        else:
            output += str('dc.' + path + '.v = ' + str(node.v) + '\n')
    for x in node.__dict__.keys():
        if isinstance(node.__dict__[x], _dcNode):
            output = _dcdump(node=node.__dict__[x],
                             path=path + bool(path)*'.' + x,
                             output=output)
    return output
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

