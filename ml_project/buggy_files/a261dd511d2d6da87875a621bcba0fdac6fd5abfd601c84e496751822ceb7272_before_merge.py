    def build_ufunc(self):
        dtypelist = []
        ptrlist = []
        if not self.nb_func:
            raise TypeError("No definition")

        # Get signature in the order they are added
        keepalive = []
        for sig in self._sigs:
            cres = self._cres[sig]
            dtypenums, ptr, env = self.build(cres)
            dtypelist.append(dtypenums)
            ptrlist.append(utils.longint(ptr))
            keepalive.append((cres.library, env))

        datlist = [None] * len(ptrlist)

        inct = len(self.sin)
        outct = len(self.sout)

        # Pass envs to fromfuncsig to bind to the lifetime of the ufunc object
        ufunc = _internal.fromfunc(self.py_func.__name__, self.py_func.__doc__,
                                ptrlist, dtypelist, inct, outct, datlist,
                                keepalive, self.identity, self.signature)
        return ufunc