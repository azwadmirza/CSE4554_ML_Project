    def _end_current_block(self):
        self._remove_unused_temporaries()
        self._insert_outgoing_phis()