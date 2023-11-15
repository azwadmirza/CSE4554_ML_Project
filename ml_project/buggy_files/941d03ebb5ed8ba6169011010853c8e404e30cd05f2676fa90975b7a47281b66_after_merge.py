    def read(self, fp, **kwargs):
        """Read a notebook from a file like object"""
        nbs = fp.read()
        if not py3compat.PY3 and not isinstance(nbs, unicode):
            nbs = py3compat.str_to_unicode(nbs)
        return self.reads(nbs, **kwargs)