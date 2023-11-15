    def __new__(cls, types):
        _HeterogeneousTuple.is_types_iterable(types)

        if types and all(t == types[0] for t in types[1:]):
            return UniTuple(dtype=types[0], count=len(types))
        else:
            return object.__new__(Tuple)