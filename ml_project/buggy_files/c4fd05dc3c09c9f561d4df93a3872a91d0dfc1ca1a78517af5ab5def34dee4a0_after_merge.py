    def match(self, func_ir, block, typemap, calltypes):
        self.raises = raises = {}
        self.tryraises = tryraises = {}
        self.block = block
        # Detect all raise statements and find which ones can be
        # rewritten
        for inst in block.find_insts((ir.Raise, ir.TryRaise)):
            if inst.exception is None:
                # re-reraise
                exc_type, exc_args = None, None
            else:
                # raise <something> => find the definition site for <something>
                const = func_ir.infer_constant(inst.exception)
                loc = inst.exception.loc
                exc_type, exc_args = self._break_constant(const, loc)
            if isinstance(inst, ir.Raise):
                raises[inst] = exc_type, exc_args
            elif isinstance(inst, ir.TryRaise):
                tryraises[inst] = exc_type, exc_args
            else:
                raise ValueError('unexpected: {}'.format(type(inst)))
        return (len(raises) + len(tryraises)) > 0