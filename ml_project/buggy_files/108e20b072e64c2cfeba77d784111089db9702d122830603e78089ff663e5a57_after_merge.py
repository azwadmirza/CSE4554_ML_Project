    def __call__(self, parent, index):
        _val = self._init(parent, index)
        if self._dimen in {1, None, UnknownSetDimen}:
            return _val
        elif _val is Set.Skip:
            return _val
        elif not _val:
            return _val

        if not isinstance(_val, collections_Sequence):
            _val = tuple(_val)
        if len(_val) == 0:
            return _val
        if isinstance(_val[0], tuple):
            return _val
        return self._tuplize(_val, parent, index)