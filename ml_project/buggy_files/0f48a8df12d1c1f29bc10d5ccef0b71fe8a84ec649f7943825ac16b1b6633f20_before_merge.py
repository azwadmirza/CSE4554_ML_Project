    def lower_block(self, block):
        """
        Lower the given block.
        """
        self.pre_block(block)
        for inst in block.body:
            self.loc = inst.loc
            defaulterrcls = partial(LoweringError, loc=self.loc)
            with new_error_context('lowering "{inst}" at {loc}', inst=inst,
                                   loc=self.loc, errcls_=defaulterrcls):
                self.lower_inst(inst)