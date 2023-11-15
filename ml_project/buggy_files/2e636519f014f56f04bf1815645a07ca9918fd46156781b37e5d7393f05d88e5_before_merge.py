    def _print_Function(self, expr):
        name = self._settings["user_functions"].get(expr.__class__)
        eargs = expr.args
        if name is None:
            from sympy.functions import conjugate
            if expr.func == conjugate:
                name = "conjg"
            else:
                name = expr.func.__name__
            if hasattr(expr, '_imp_') and isinstance(expr._imp_, C.Lambda):
                # inlined function.
                # the expression is printed with _print to avoid loops
                return self._print(expr._imp_(*eargs))
            if expr.func.__name__ not in self._implicit_functions:
                self._not_supported.add(expr)
            else:
                # convert all args to floats
                eargs = map(N, eargs)
        return "%s(%s)" % (name, self.stringify(eargs, ", "))