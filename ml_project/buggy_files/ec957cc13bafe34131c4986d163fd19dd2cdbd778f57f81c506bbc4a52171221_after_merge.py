    def __pow__(self, other, mod=None):
        if mod is None:
            return self._pow(other)
        try:
            _self, other, mod = as_int(self), as_int(other), as_int(mod)
            if other >= 0:
                return pow(_self, other, mod)
            else:
                from sympy.core.numbers import mod_inverse
                return mod_inverse(pow(_self, -other, mod), mod)
        except ValueError:
            power = self._pow(other)
            try:
                return power%mod
            except TypeError:
                return NotImplemented