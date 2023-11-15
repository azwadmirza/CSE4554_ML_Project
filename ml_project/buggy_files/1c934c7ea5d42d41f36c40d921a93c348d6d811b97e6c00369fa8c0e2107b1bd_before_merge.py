    def match(self, interp, block, typemap, calltypes):
        """
        Look for potential macros for expand and store their expansions.
        """
        self.block = block
        self.rewrites = rewrites = {}

        for inst in block.body:
            if isinstance(inst, ir.Assign):
                rhs = inst.value
                if (isinstance(rhs, ir.Expr) and rhs.op == 'call'
                    and isinstance(rhs.func, ir.Var)):
                    # Is it a callable macro?
                    try:
                        const = interp.infer_constant(rhs.func)
                    except errors.ConstantInferenceError:
                        continue
                    if isinstance(const, Macro):
                        assert const.callable
                        new_expr = self._expand_callable_macro(interp, rhs,
                                                               const, rhs.loc)
                        rewrites[rhs] = new_expr

                elif isinstance(rhs, ir.Expr) and rhs.op == 'getattr':
                    # Is it a non-callable macro looked up as a constant attribute?
                    try:
                        const = interp.infer_constant(inst.target)
                    except errors.ConstantInferenceError:
                        continue
                    if isinstance(const, Macro) and not const.callable:
                        new_expr = self._expand_non_callable_macro(const, rhs.loc)
                        rewrites[rhs] = new_expr

        return len(rewrites) > 0