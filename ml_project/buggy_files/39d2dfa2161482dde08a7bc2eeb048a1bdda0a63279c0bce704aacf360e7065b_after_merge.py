    def ensure_directories(self):
        return super(PyPy, self).ensure_directories() | {self.lib_pypy}