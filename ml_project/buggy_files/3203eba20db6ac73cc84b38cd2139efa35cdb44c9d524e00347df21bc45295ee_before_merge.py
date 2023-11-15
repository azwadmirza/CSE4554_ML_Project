    def __init__(self, py_func, identity=None, cache=False, targetoptions={}):
        if isinstance(py_func, Dispatcher):
            py_func = py_func.py_func
        self.targetoptions = targetoptions.copy()
        kws = {}
        kws['identity'] = ufuncbuilder.parse_identity(identity)

        dispatcher = jit(target='npyufunc', cache=cache)(py_func)
        super(DUFunc, self).__init__(dispatcher, **kws)
        # Loop over a copy of the keys instead of the keys themselves,
        # since we're changing the dictionary while looping.
        self._install_type()
        self._lower_me = DUFuncLowerer(self)
        self._install_cg()
        self.__name__ = py_func.__name__
        self.__doc__ = py_func.__doc__