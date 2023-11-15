    def build_ufunc(self):
        with global_compiler_lock:
            dtypelist = []
            ptrlist = []
            if not self.nb_func:
                raise TypeError("No definition")

            # Get signature in the order they are added
            keepalive = []
            cres = None
            for sig in self._sigs:
                cres = self._cres[sig]
                dtypenums, ptr, env = self.build(cres, sig)
                dtypelist.append(dtypenums)
                ptrlist.append(utils.longint(ptr))
                keepalive.append((cres.library, env))

            datlist = [None] * len(ptrlist)

            if cres is None:
                if PYVERSION >= (3, 0):
                    argspec = inspect.getfullargspec(self.py_func)
                else:
                    argspec = inspect.getargspec(self.py_func)
                inct = len(argspec.args)
            else:
                inct = len(cres.signature.args)
            outct = 1

            # Becareful that fromfunc does not provide full error checking yet.
            # If typenum is out-of-bound, we have nasty memory corruptions.
            # For instance, -1 for typenum will cause segfault.
            # If elements of type-list (2nd arg) is tuple instead,
            # there will also memory corruption. (Seems like code rewrite.)
            ufunc = _internal.fromfunc(self.py_func.__name__, self.py_func.__doc__,
                                    ptrlist, dtypelist, inct, outct, datlist,
                                    keepalive, self.identity)

            return ufunc