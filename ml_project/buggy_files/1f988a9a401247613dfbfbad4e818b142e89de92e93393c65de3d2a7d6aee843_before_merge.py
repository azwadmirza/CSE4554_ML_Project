    def match(self, interp, block, typemap, calltypes):
        self.setitems = setitems = {}
        self.block = block
        # Detect all setitem statements and find which ones can be
        # rewritten
        for inst in block.find_insts(ir.SetItem):
            try:
                const = interp.infer_constant(inst.index)
            except errors.ConstantInferenceError:
                continue
            setitems[inst] = const

        return len(setitems) > 0