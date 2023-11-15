    def __iter__(self):
        current_from_block = self.from_block
        current_to_block = min(self.from_block + self.max_blocks_per_call, self.to_block)
        while current_from_block < current_to_block:
            for event_record in self.event_filter(from_block=current_from_block,
                                                  to_block=current_to_block,
                                                  **self.argument_filters):
                yield event_record
            current_from_block = current_to_block
            # update the 'to block' to the lesser of either the next `max_blocks_per_call` blocks,
            # or the remainder of blocks
            current_to_block = min(current_from_block + self.max_blocks_per_call, self.to_block)