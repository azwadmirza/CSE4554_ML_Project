    def __init__(self, arg_count, py_func):
        self.tm = default_type_manager
        _dispatcher.Dispatcher.__init__(self, self.tm.get_pointer(), arg_count)

        # A mapping of signatures to entry points
        self.overloads = {}
        # A mapping of signatures to compile results
        self._compileinfos = {}
        # A list of nopython signatures
        self._npsigs = []

        self.py_func = py_func
        # other parts of Numba assume the old Python 2 name for code object
        self.func_code = get_code_object(py_func)
        # but newer python uses a different name
        self.__code__ = self.func_code

        self.doc = py_func.__doc__
        self._compiling = False

        utils.finalize(self, self._make_finalizer())