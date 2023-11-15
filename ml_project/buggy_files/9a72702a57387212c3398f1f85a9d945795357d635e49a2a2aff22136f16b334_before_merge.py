        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.tag = self._root.IfdField.TagEnum(self._io.read_u2le())
            self.field_type = self._root.IfdField.FieldTypeEnum(self._io.read_u2le())
            self.length = self._io.read_u4le()
            self.ofs_or_data = self._io.read_u4le()