    def pop_block(self):
        b = self._blockstack.pop()
        new_stack = self._stack[:b['stack_depth']]
        _logger.debug("POP_BLOCK:\nold_stack=%s\nnew_stack=%s", self._stack,
                      new_stack)
        self._stack = new_stack