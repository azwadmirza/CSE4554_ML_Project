    def _intersect(self, other):
        from sympy.solvers.diophantine import diophantine
        if self.base_set is S.Integers:
            g = None
            if isinstance(other, ImageSet) and other.base_set is S.Integers:
                g = other.lamda.expr
                m = other.lamda.variables[0]
            elif other is S.Integers:
                m = g = Dummy('x')
            if g is not None:
                f = self.lamda.expr
                n = self.lamda.variables[0]
                # Diophantine sorts the solutions according to the alphabetic
                # order of the variable names, since the result should not depend
                # on the variable name, they are replaced by the dummy variables
                # below
                a, b = Dummy('a'), Dummy('b')
                f, g = f.subs(n, a), g.subs(m, b)
                solns_set = diophantine(f - g)
                if solns_set == set():
                    return EmptySet()
                solns = list(diophantine(f - g))

                if len(solns) != 1:
                    return

                # since 'a' < 'b', select soln for n
                nsol = solns[0][0]
                t = nsol.free_symbols.pop()
                return imageset(Lambda(n, f.subs(a, nsol.subs(t, n))), S.Integers)

        if other == S.Reals:
            from sympy.solvers.solveset import solveset_real
            from sympy.core.function import expand_complex
            if len(self.lamda.variables) > 1:
                return None

            f = self.lamda.expr
            n = self.lamda.variables[0]

            n_ = Dummy(n.name, real=True)
            f_ = f.subs(n, n_)

            re, im = f_.as_real_imag()
            im = expand_complex(im)

            return imageset(Lambda(n_, re),
                            self.base_set.intersect(
                                solveset_real(im, n_)))