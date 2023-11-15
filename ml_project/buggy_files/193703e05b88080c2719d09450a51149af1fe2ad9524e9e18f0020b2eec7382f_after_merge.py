    def wrapper(self, other):
        comparable_types = (VersionInfo, dict, tuple, list, str)
        if not isinstance(other, comparable_types):
            raise TypeError(
                "other type %r must be in %r" % (type(other), comparable_types)
            )
        return operator(self, other)