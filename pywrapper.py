
def logger(name):
    print('excuting', name)
    def wrap(func):
        def wrapped(*args, **kwargs):
            print (args)
            print (kwargs)
            func(*args, **kwargs)
        return wrapped
    return wrap

@logger('foofunc')
def foofunc(foo, bar):
    print('running foo')

foofunc('foo', 'bar')

