    def unfold_region(self, block, start_line, end_line):
        """Unfold region spanned by *start_line* and *end_line*."""
        while block.blockNumber() < end_line and block.isValid():
            current_line = block.blockNumber()
            block.setVisible(True)
            get_next = True
            if (current_line in self.folding_regions
                    and current_line != start_line):
                block_end = self.folding_regions[current_line]
                if self.folding_status[current_line]:
                    # Skip setting visible blocks until the block is done
                    get_next = False
                    block = self._get_block_until_line(block, block_end - 1)
                    # pass
            if get_next:
                block = block.next()