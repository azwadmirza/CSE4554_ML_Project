    def get_top_block(self, kind):
        for bs in reversed(self._blockstack):
            if bs['kind'] == kind:
                return bs