    def from_types(cls, tys, pyclass=None):
        """
        Instantiate the right tuple type for the given element types.
        """
        if pyclass is not None and pyclass is not tuple:
            # A subclass => is it a namedtuple?
            assert issubclass(pyclass, tuple)
            if hasattr(pyclass, "_asdict"):
                tys = tuple(map(unliteral, tys))
                homogeneous = is_homogeneous(*tys)
                if homogeneous:
                    return NamedUniTuple(tys[0], len(tys), pyclass)
                else:
                    return NamedTuple(tys, pyclass)
        else:
            # non-named tuple
            homogeneous = is_homogeneous(*tys)
            if homogeneous:
                return UniTuple(tys[0], len(tys))
            else:
                return Tuple(tys)