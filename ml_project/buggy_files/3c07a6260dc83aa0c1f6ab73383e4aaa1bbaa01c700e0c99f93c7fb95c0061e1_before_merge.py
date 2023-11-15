        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.num_fields = self._io.read_u2le()
            self.fields = [None] * (self.num_fields)
            for i in range(self.num_fields):
                self.fields[i] = self._root.IfdField(self._io, self, self._root)

            self.next_ifd_ofs = self._io.read_u4le()