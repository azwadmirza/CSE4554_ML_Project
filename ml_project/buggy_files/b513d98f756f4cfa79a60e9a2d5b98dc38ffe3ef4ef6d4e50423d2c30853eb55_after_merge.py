    def match(self, func_ir, block, typemap, calltypes):
        self.consts = consts = {}
        self.block = block
        for inst in block.find_insts(ir.Print):
            if inst.consts:
                # Already rewritten
                continue
            for idx, var in enumerate(inst.args):
                try:
                    const = func_ir.infer_constant(var)
                except errors.ConstantInferenceError:
                    continue
                consts.setdefault(inst, {})[idx] = const

        return len(consts) > 0