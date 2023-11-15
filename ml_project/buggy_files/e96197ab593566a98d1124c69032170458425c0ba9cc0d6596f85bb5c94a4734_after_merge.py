    def _eval_imageset(self, f):
        expr = f.expr
        if not isinstance(expr, Expr):
            return

        if len(f.variables) > 1:
            return

        n = f.variables[0]

        # f(x) + c and f(-x) + c cover the same integers
        # so choose the form that has the fewest negatives
        c = f(0)
        fx = f(n) - c
        f_x = f(-n) - c
        neg_count = lambda e: sum(_coeff_isneg(_) for _ in Add.make_args(e))
        if neg_count(f_x) < neg_count(fx):
            expr = f_x + c

        a = Wild('a', exclude=[n])
        b = Wild('b', exclude=[n])
        match = expr.match(a*n + b)
        if match and match[a]:
            # canonical shift
            expr = match[a]*n + match[b] % match[a]

        if expr != f.expr:
            return ImageSet(Lambda(n, expr), S.Integers)