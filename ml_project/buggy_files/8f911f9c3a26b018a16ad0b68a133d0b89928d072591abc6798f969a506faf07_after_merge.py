    def op_POP_BLOCK(self, inst, kind=None):
        if kind is None:
            self.syntax_blocks.pop()
        elif kind == 'try':
            self._insert_try_block_end()