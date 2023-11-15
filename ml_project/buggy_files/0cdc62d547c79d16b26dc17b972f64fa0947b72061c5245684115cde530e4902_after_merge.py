    def _match_array_expr(self, instr, expr, target_name):
        """
        Find whether the given assignment (*instr*) of an expression (*expr*)
        to variable *target_name* is an array expression.
        """
        # We've matched a subexpression assignment to an
        # array variable.  Now see if the expression is an
        # array expression.
        expr_op = expr.op
        array_assigns = self.array_assigns

        if ((expr_op in ('unary', 'binop')) and (
                expr.fn in npydecl.supported_array_operators)):
            # It is an array operator that maps to a ufunc.
            # check that all args have internal types
            if all(self.typemap[var.name].is_internal
                   for var in expr.list_vars()):
                array_assigns[target_name] = instr

        elif ((expr_op == 'call') and (expr.func.name in self.typemap)):
            # It could be a match for a known ufunc call.
            func_type = self.typemap[expr.func.name]
            if isinstance(func_type, types.Function):
                func_key = func_type.typing_key
                if _is_ufunc(func_key):
                    # If so, check whether an explicit output is passed.
                    if not self._has_explicit_output(expr, func_key):
                        # If not, match it as a (sub)expression.
                        array_assigns[target_name] = instr