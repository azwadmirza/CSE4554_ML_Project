    def get_docs(self, key, default=None):
        """Gets the documentation for the environment variable."""
        vd = self._vars.get(key, default)
        if vd is None:
            vd = Var(default="", doc_default="")
        if vd.doc_default is DefaultNotGiven:
            dval = pprint.pformat(vd.default)
            vd = vd._replace(doc_default=dval)
        return vd