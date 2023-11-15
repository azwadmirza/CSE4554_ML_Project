    def pre_block(self, block):
        from numba.unsafe import eh

        super(Lower, self).pre_block(block)

        # Detect if we are in a TRY block by looking for a call to
        # `eh.exception_check`.
        for call in block.find_exprs(op='call'):
            defn = ir_utils.guard(
                ir_utils.get_definition, self.func_ir, call.func,
            )
            if defn is not None and isinstance(defn, ir.Global):
                if defn.value is eh.exception_check:
                    if isinstance(block.terminator, ir.Branch):
                        targetblk = self.blkmap[block.terminator.truebr]
                        # NOTE: This hacks in an attribute for call_conv to
                        #       pick up. This hack is no longer needed when
                        #       all old-style implementations are gone.
                        self.builder._in_try_block = {'target': targetblk}
                        break