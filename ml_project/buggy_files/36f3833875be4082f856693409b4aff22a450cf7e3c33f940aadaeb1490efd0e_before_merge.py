    def from_types(cls, tys, pyclass=None):
        """
        Instantiate the right tuple type for the given element types.
        """
        homogeneous = False
        if tys:
            first = tys[0]
            for ty in tys[1:]:
                if ty != first:
                    break
            else:
                homogeneous = True

        if pyclass is not None and pyclass is not tuple:
            # A subclass => is it a namedtuple?
            assert issubclass(pyclass, tuple)
            if hasattr(pyclass, "_asdict"):
                if homogeneous:
                    return NamedUniTuple(first, len(tys), pyclass)
                else:
                    return NamedTuple(tys, pyclass)
        if homogeneous:
            return UniTuple(first, len(tys))
        else:
            return Tuple(tys)