    def readFile(self, path=None, s=None):

        if not s:
            with open(path, 'rb') as f:
                s = f.read()
        # s = s.replace(b'\x0c', b'').replace(b'0x00', b'')
        s = s.translate(None, self.translate_table)
            # Fix #1036 and #1046.
        return self.readWithElementTree(path, s)