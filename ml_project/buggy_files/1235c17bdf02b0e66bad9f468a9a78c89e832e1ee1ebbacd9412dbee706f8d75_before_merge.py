    def relpath(self, other):
        return self.__class__(
            os.path.relpath(fspath_py35(self), fspath_py35(other))
        )