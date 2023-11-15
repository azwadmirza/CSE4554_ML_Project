    def wrapper(self: "Version", other: Comparable) -> bool:
        comparable_types = (
            Version,
            dict,
            tuple,
            list,
            *String.__args__,  # type: ignore
        )
        if not isinstance(other, comparable_types):
            raise TypeError(
                "other type %r must be in %r" % (type(other), comparable_types)
            )
        return operator(self, other)