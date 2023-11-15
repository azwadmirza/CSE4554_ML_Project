    def _build_impl(self, cache_key, args, kws):
        """Build and cache the implementation.

        Given the positional (`args`) and keyword arguments (`kws`), obtains
        the `overload` implementation and wrap it in a Dispatcher object.
        The expected argument types are returned for use by type-inference.
        The expected argument types are only different from the given argument
        types if there is an imprecise type in the given argument types.

        Parameters
        ----------
        cache_key : hashable
            The key used for caching the implementation.
        args : Tuple[Type]
            Types of positional argument.
        kws : Dict[Type]
            Types of keyword argument.

        Returns
        -------
        disp, args :
            On success, returns `(Dispatcher, Tuple[Type])`.
            On failure, returns `(None, None)`.

        """
        from numba import jit

        def normalize_args(pyfunc, args, kws):
            pysig = utils.pysignature(pyfunc)
            ba = pysig.bind(*args, **kws)
            starargs = None
            for i, (k, parm) in enumerate(pysig.parameters.items()):
                if parm.kind == parm.VAR_POSITIONAL and k in ba.arguments:
                    starargs = ba.arguments[k]
                    del ba.arguments[k]

            new_args = ba.args
            if starargs is not None:
                if (len(starargs) and isinstance(starargs[0], types.Tuple) and
                        len(starargs[0]) == 0):
                    # empty tuple means no starargs
                    pass
                else:
                    new_args += starargs

            new_kws = ba.kwargs
            return new_args, new_kws

        # args, kws = normalize_args(self._overload_func, args, kws)

        # Get the overload implementation for the given types
        ovf_result = self._overload_func(*args, **kws)
        if ovf_result is None:
            # No implementation => fail typing
            self._impl_cache[cache_key] = None, None
            return None, None
        elif isinstance(ovf_result, tuple):
            # The implementation returned a signature that the type-inferencer
            # should be using.
            sig, pyfunc = ovf_result
            args = sig.args
            cache_key = None            # don't cache
        else:
            # Regular case
            pyfunc = ovf_result

        # Check type of pyfunc
        if not isinstance(pyfunc, FunctionType):
            msg = ("Implementator function returned by `@overload` "
                   "has an unexpected type.  Got {}")
            raise AssertionError(msg.format(pyfunc))

        # check that the typing and impl sigs match up
        if self._strict:
            self._validate_sigs(self._overload_func, pyfunc)
        # Make dispatcher
        jitdecor = jit(nopython=True, **self._jit_options)
        disp = jitdecor(pyfunc)
        if cache_key is not None:
            self._impl_cache[cache_key] = disp, args
        return disp, args