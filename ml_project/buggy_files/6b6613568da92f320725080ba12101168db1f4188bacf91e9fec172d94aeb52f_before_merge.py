    def url(self):
        return "{}://{}{}".format(self.scheme, self.netloc, self._spath)