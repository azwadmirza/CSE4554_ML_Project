    def fork(self, pc, npop=0):
        """Fork the state
        """
        assert 0 <= npop <= len(self._stack)
        nstack = len(self._stack) - npop
        stack = self._stack[:nstack]
        self._outedges.append(Edge(pc=pc, stack=stack,
                                   blockstack=tuple(self._blockstack)))
        self.terminate()