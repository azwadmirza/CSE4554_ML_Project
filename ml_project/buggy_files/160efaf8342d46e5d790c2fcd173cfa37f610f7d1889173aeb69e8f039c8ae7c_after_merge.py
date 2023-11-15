    def _infer_call(self, func, expr):
        if expr.kws or expr.vararg:
            self._fail(expr)
        # Check supported callables
        _slice = func in (slice,)
        _exc = isinstance(func, type) and issubclass(func, BaseException)
        if _slice or _exc:
            args = [self.infer_constant(a.name, loc=expr.loc) for a in
                    expr.args]
            if _slice:
                return func(*args)
            elif _exc:
                # If the exception class is user defined it may implement a ctor
                # that does not pass the args to the super. Therefore return the
                # raw class and the args so this can be instantiated at the call
                # site in the way the user source expects it to be.
                return func, args
            else:
                assert 0, 'Unreachable'

        self._fail(expr)