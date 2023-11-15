    def _shared_lib_to(self):
        return super(PyPy3, self)._shared_lib_to() + [self.stdlib.parent.parent]