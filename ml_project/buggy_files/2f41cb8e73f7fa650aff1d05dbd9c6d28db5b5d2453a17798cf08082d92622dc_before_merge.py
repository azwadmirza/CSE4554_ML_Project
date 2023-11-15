    def getargvlist(self, name, default="", replace=True):
        s = self.getstring(name, default, replace=False)
        return _ArgvlistReader.getargvlist(self, s, replace=replace)