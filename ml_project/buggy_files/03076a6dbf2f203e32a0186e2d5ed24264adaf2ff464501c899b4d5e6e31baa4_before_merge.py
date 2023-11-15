    def _start_new_block(self, offset):
        oldblock = self.current_block
        self.insert_block(offset)
        # Ensure the last block is terminated
        if oldblock is not None and not oldblock.is_terminated:
            jmp = ir.Jump(offset, loc=self.loc)
            oldblock.append(jmp)
        # Get DFA block info
        self.dfainfo = self.dfa.infos[self.current_block_offset]
        self.assigner = Assigner()
        # Check out-of-scope syntactic-block
        while self.syntax_blocks:
            if offset >= self.syntax_blocks[-1].exit:
                self.syntax_blocks.pop()
            else:
                break