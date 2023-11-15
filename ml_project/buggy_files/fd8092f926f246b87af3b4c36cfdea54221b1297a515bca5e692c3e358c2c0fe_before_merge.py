    def readFile(self, path=None, s=None):

        if not s:
            with open(path, 'rb') as f:
                s = f.read()
        return self.readWithElementTree(path, s)