    def match(self, func_ir, block, typemap, calltypes):
        self.getitems = getitems = {}
        self.block = block
        # Detect all getitem expressions and find which ones can be
        # rewritten
        for expr in block.find_exprs(op='getitem'):
            if expr.op == 'getitem':
                try:
                    const = func_ir.infer_constant(expr.index)
                except errors.ConstantInferenceError:
                    continue
                getitems[expr] = const

        return len(getitems) > 0