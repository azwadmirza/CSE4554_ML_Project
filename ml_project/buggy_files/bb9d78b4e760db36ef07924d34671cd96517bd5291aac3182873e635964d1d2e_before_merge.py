    def _print_Indexed(self, expr):
        # calculate index for 1d array
        dims = expr.shape
        inds = [ i.label for i in expr.indices ]
        elem = S.Zero
        offset = S.One
        for i in reversed(range(expr.rank)):
            elem += offset*inds[i]
            offset *= dims[i]
        return "%s[%s]" % (self._print(expr.base.label), self._print(elem))