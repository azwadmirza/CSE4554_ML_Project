    def match(self, interp, block, typemap, calltypes):
        self.prints = prints = {}
        self.block = block
        # Find all assignments with a right-hand print() call
        for inst in block.find_insts(ir.Assign):
            if isinstance(inst.value, ir.Expr) and inst.value.op == 'call':
                expr = inst.value
                if expr.kws:
                    # Only positional args are supported
                    continue
                try:
                    callee = interp.infer_constant(expr.func)
                except errors.ConstantInferenceError:
                    continue
                if callee is print:
                    prints[inst] = expr
        return len(prints) > 0