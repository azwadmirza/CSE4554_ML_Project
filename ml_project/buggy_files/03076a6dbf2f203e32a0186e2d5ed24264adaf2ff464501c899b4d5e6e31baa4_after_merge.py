    def _start_new_block(self, offset):
        oldblock = self.current_block
        self.insert_block(offset)
        # Ensure the last block is terminated
        if oldblock is not None and not oldblock.is_terminated:
            # Handle ending try block.
            tryblk = self.dfainfo.active_try_block
            # If there's an active try-block and the handler block is live.
            if tryblk is not None and tryblk['end'] in self.cfa.graph.nodes():
                # We are in a try-block, insert a branch to except-block.
                # This logic cannot be in self._end_current_block()
                # because we the non-raising next block-offset.
                branch = ir.Branch(
                    cond=self.get('$exception_check'),
                    truebr=tryblk['end'],
                    falsebr=offset,
                    loc=self.loc,
                )
                oldblock.append(branch)
            # Handle normal case
            else:
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