    def get_top_block(self, kind):
        """Find the first block that matches *kind*
        """
        kind = BlockKind(kind)
        for bs in reversed(self._blockstack):
            if bs['kind'] == kind:
                return bs