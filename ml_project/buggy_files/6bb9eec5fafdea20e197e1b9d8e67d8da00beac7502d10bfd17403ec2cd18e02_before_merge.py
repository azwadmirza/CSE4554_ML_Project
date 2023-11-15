    def push_block(self, synblk):
        d = synblk.copy()
        d['stack_depth'] = len(self._stack)
        self._blockstack.append(d)