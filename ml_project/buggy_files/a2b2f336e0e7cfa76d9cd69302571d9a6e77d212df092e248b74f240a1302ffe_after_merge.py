    def _contains(self, other):
        """
        Tests whether an element, other, is in the set.

        Relies on Python's set class. This tests for object equality
        All inputs are sympified

        Examples
        ========

        >>> from sympy import FiniteSet
        >>> 1 in FiniteSet(1, 2)
        True
        >>> 5 in FiniteSet(1, 2)
        False

        """
        r = false
        for e in self._elements:
            t = Eq(e, other, evaluate=True)
            if isinstance(t, Eq):
                t = t.simplify()
            if t == true:
                return t
            elif t != false:
                r = None
        return r