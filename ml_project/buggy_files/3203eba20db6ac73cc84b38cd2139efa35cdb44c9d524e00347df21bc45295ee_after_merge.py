    def __init__(self, py_func, identity=None, cache=False, targetoptions={}):
        if isinstance(py_func, Dispatcher):
            py_func = py_func.py_func
        dispatcher = jit(target='npyufunc', cache=cache, **targetoptions)(py_func)
        self._initialize(dispatcher, identity)