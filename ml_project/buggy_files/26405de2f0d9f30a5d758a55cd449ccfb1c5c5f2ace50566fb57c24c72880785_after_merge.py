    def match(self, func_ir, block, typemap, calltypes):
        self.raises = raises = {}
        self.block = block
        # Detect all raise statements and find which ones can be
        # rewritten
        for inst in block.find_insts(ir.Raise):
            if inst.exception is None:
                # re-reraise
                exc_type, exc_args = None, None
            else:
                # raise <something> => find the definition site for <something>
                const = func_ir.infer_constant(inst.exception)
                exc_type, exc_args = self._break_constant(const)
            raises[inst] = exc_type, exc_args

        return len(raises) > 0