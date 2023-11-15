    def fork(self, pc, npop=0, npush=0, extra_block=None):
        """Fork the state
        """
        # Handle changes on the stack
        stack = list(self._stack)
        if npop:
            assert 0 <= npop <= len(self._stack)
            nstack = len(self._stack) - npop
            stack = stack[:nstack]
        if npush:
            assert 0 <= npush
            for i in range(npush):
                stack.append(self.make_temp())
        # Handle changes on the blockstack
        blockstack = list(self._blockstack)
        if extra_block:
            blockstack.append(extra_block)
        self._outedges.append(Edge(
            pc=pc, stack=tuple(stack), npush=npush,
            blockstack=tuple(blockstack),
        ))
        self.terminate()