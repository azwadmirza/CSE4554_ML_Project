def comparator(operator):
    """Wrap a VersionInfo binary op method in a type-check."""

    @wraps(operator)
    def wrapper(self, other):
        comparable_types = (VersionInfo, dict, tuple)
        if not isinstance(other, comparable_types):
            raise TypeError(
                "other type %r must be in %r" % (type(other), comparable_types)
            )
        return operator(self, other)

    return wrapper