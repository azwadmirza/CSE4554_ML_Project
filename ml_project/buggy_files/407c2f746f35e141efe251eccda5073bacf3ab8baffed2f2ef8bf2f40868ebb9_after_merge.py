    def __setstate__(self, state):
        frames, items, major, minor, fv, kind = state

        self.default_fill_value = fv
        self.default_kind = kind
        self._items = _ensure_index(com._unpickle_array(items))
        self._major_axis = _ensure_index(com._unpickle_array(major))
        self._minor_axis = _ensure_index(com._unpickle_array(minor))
        self._frames = frames