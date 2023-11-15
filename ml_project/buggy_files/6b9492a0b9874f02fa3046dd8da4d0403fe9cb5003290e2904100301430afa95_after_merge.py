    def _end_current_block(self):
        # Handle try block
        if not self.current_block.is_terminated:
            tryblk = self.dfainfo.active_try_block
            if tryblk is not None:
                self._insert_exception_check()
        # Handle normal block cleanup
        self._remove_unused_temporaries()
        self._insert_outgoing_phis()