    def ensure_directories(self):
        dirs = super(PyPy, self).ensure_directories()
        dirs.add(self.lib_pypy)
        return dirs