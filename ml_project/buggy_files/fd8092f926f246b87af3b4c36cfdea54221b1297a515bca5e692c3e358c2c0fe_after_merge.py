    def readFile(self, path=None, s=None):

        if not s:
            with open(path, 'rb') as f:
                s = f.read()
        s = s.replace(b'\x0c', b'')
            # Fix #1036.
        return self.readWithElementTree(path, s)