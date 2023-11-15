    def build(self, cres):
        """
        Returns (dtype numbers, function ptr, EnvironmentObject)
        """
        # Buider wrapper for ufunc entry point
        signature = cres.signature
        ptr, env, wrapper_name = build_gufunc_wrapper(self.py_func, cres, self.sin, self.sout,
                                        cache=self.cache)

        # Get dtypes
        dtypenums = []
        for a in signature.args:
            if isinstance(a, types.Array):
                ty = a.dtype
            else:
                ty = a
            dtypenums.append(as_dtype(ty).num)
        return dtypenums, ptr, env