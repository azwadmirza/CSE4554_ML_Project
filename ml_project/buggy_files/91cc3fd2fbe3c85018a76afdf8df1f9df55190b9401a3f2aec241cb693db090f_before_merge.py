        def data(self):
            if hasattr(self, '_m_data'):
                return self._m_data if hasattr(self, '_m_data') else None

            if not self.is_immediate_data:
                io = self._root._io
                _pos = io.pos()
                io.seek(self.ofs_or_data)
                self._m_data = io.read_bytes(self.byte_length)
                io.seek(_pos)

            return self._m_data if hasattr(self, '_m_data') else None