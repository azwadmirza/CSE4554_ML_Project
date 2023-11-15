    def get_block_operator(self):
        """Determine the immediate parent boolean operator for a filter"""
        # Top level operator is `and`
        block_stack = ['and']
        for f in self.manager.iter_filters(block_end=True):
            if f is None:
                block_stack.pop()
                continue
            if f.type in ('and', 'or', 'not'):
                block_stack.append(f.type)
            if f == self:
                break
        return block_stack[-1]