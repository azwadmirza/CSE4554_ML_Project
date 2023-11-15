    def _contains(self, other):
        from sympy.matrices import Matrix
        from sympy.solvers.solveset import solveset, linsolve
        from sympy.utilities.iterables import iterable, cartes
        L = self.lamda
        if self._is_multivariate():
            if not iterable(L.expr):
                if iterable(other):
                    return S.false
                return other.as_numer_denom() in self.func(
                    Lambda(L.variables, L.expr.as_numer_denom()), self.base_set)
            if len(L.expr) != len(self.lamda.variables):
                raise NotImplementedError(filldedent('''
    Dimensions of input and output of Lambda are different.'''))
            eqs = [expr - val for val, expr in zip(other, L.expr)]
            variables = L.variables
            free = set(variables)
            if all(i.is_number for i in list(Matrix(eqs).jacobian(variables))):
                solns = list(linsolve([e - val for e, val in
                zip(L.expr, other)], variables))
            else:
                syms = [e.free_symbols & free for e in eqs]
                solns = {}
                for i, (e, s, v) in enumerate(zip(eqs, syms, other)):
                    if not s:
                        if e != v:
                            return S.false
                        solns[vars[i]] = [v]
                        continue
                    elif len(s) == 1:
                        sy = s.pop()
                        sol = solveset(e, sy)
                        if sol is S.EmptySet:
                            return S.false
                        elif isinstance(sol, FiniteSet):
                            solns[sy] = list(sol)
                        else:
                            raise NotImplementedError
                    else:
                        raise NotImplementedError
                solns = cartes(*[solns[s] for s in variables])
        else:
            # assume scalar -> scalar mapping
            solnsSet = solveset(L.expr - other, L.variables[0])
            if solnsSet.is_FiniteSet:
                solns = list(solnsSet)
            else:
                raise NotImplementedError(filldedent('''
                Determining whether an ImageSet contains %s has not
                been implemented.''' % func_name(other)))
        for soln in solns:
            try:
                if soln in self.base_set:
                    return S.true
            except TypeError:
                return self.base_set.contains(soln.evalf())
        return S.false