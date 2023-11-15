    def get_encoding(self):
        while 1:
            try:
                (cid, name) = self.nextobject()
            except PSEOF:
                break
            try:
                self._cid2unicode[cid] = name2unicode(name)
            except KeyError:
                pass
        return self._cid2unicode