    def push_block(self, synblk):
        """Push a block to blockstack
        """
        assert 'stack_depth' in synblk
        self._blockstack.append(synblk)