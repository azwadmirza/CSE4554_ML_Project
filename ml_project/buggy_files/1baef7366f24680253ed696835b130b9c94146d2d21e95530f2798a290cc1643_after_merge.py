    def infer_constant(self, name, loc=None):
        """
        Infer a constant value for the given variable *name*.
        If no value can be inferred, numba.errors.ConstantInferenceError
        is raised.
        """
        if name not in self._cache:
            try:
                self._cache[name] = (True, self._do_infer(name))
            except ConstantInferenceError as exc:
                # Store the exception args only, to avoid keeping
                # a whole traceback alive.
                self._cache[name] = (False, (exc.__class__, exc.args))
        success, val = self._cache[name]
        if success:
            return val
        else:
            exc, args = val
            if issubclass(exc, NumbaError):
                raise exc(*args, loc=loc)
            else:
                raise exc(*args)