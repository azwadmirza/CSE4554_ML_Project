    def get_block_operator(self):
        """Determine the immediate parent boolean operator for a filter"""
        # Top level operator is `and`
        block = self.get_block_parent()
        if block.type in ('and', 'or', 'not'):
            return block.type
        return 'and'