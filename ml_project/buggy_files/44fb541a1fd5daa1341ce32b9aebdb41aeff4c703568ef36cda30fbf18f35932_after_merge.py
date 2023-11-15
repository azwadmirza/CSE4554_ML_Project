    def write(self, nb, fp, **kwargs):
        """Write a notebook to a file like object"""
        nbs = self.writes(nb,**kwargs)
        if not py3compat.PY3 and not isinstance(nbs, unicode):
            # this branch is likely only taken for JSON on Python 2
            nbs = py3compat.str_to_unicode(nbs)
        return fp.write(nbs)