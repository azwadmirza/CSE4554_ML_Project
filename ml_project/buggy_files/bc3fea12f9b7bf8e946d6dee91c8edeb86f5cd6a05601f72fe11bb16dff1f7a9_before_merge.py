    def match(self, interp, block, typemap, calltypes):
        self.static_lhs = {}
        self.static_rhs = {}
        self.block = block
        # Find binop expressions with a constant lhs or rhs
        for expr in block.find_exprs(op='binop'):
            try:
                if (expr.fn in self.rhs_operators
                    and expr.static_rhs is ir.UNDEFINED):
                    self.static_rhs[expr] = interp.infer_constant(expr.rhs)
            except errors.ConstantInferenceError:
                continue

        return len(self.static_lhs) > 0 or len(self.static_rhs) > 0