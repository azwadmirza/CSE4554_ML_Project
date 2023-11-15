    def get_docs(self, key, default=None):
        """Gets the documentation for the environment variable."""
        vd = self._vars.get(key, None)
        if vd is None:
            if default is None:
                default = Var()
            return default
        if vd.doc_default is DefaultNotGiven:
            dval = pprint.pformat(self._vars.get(key, "<default not set>").default)
            vd = vd._replace(doc_default=dval)
        return vd