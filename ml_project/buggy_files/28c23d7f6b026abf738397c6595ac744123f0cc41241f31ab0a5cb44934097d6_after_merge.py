    def op_RAISE_VARARGS(self, inst, exc):
        if exc is not None:
            exc = self.get(exc)
        tryblk = self.dfainfo.active_try_block
        if tryblk is not None:
            # In a try block
            stmt = ir.TryRaise(exception=exc, loc=self.loc)
            self.current_block.append(stmt)
            self._insert_try_block_end()
            self.current_block.append(ir.Jump(tryblk['end'], loc=self.loc))
        else:
            # Not in a try block
            stmt = ir.Raise(exception=exc, loc=self.loc)
            self.current_block.append(stmt)