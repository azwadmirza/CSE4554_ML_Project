    def get_substituted_expressions(self, variables=None,
                                    include_subexpressions=False):
        '''
        Return a list of ``(varname, expr)`` tuples, containing all
        differential equations (and optionally subexpressions) with all the
        subexpression variables substituted with the respective expressions.

        Parameters
        ----------
        variables : dict, optional
            A mapping of variable names to `Variable`/`Function` objects.
        include_subexpressions : bool
            Whether also to return substituted subexpressions. Defaults to
            ``False``.

        Returns
        -------
        expr_tuples : list of (str, `CodeString`)
            A list of ``(varname, expr)`` tuples, where ``expr`` is a
            `CodeString` object with all subexpression variables substituted
            with the respective expression.
        '''
        if self._substituted_expressions is None:
            self._substituted_expressions = []
            substitutions = {}
            for eq in self.ordered:
                # Skip parameters
                if eq.expr is None:
                    continue

                new_sympy_expr = str_to_sympy(eq.expr.code, variables).xreplace(substitutions)
                new_str_expr = sympy_to_str(new_sympy_expr)
                expr = Expression(new_str_expr)

                if eq.type == SUBEXPRESSION:
                    substitutions.update({sympy.Symbol(eq.varname, real=True): str_to_sympy(expr.code, variables)})
                    self._substituted_expressions.append((eq.varname, expr))
                elif eq.type == DIFFERENTIAL_EQUATION:
                    #  a differential equation that we have to check
                    self._substituted_expressions.append((eq.varname, expr))
                else:
                    raise AssertionError('Unknown equation type %s' % eq.type)

        if include_subexpressions:
            return self._substituted_expressions
        else:
            return [(name, expr) for name, expr in self._substituted_expressions
                    if self[name].type == DIFFERENTIAL_EQUATION]