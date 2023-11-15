    def pop_block(self):
        """Pop a block and unwind the stack
        """
        b = self._blockstack.pop()
        self.reset_stack(b['stack_depth'])
        return b