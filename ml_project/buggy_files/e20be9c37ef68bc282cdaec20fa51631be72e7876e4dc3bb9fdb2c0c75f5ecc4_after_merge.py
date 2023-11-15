    def blocks(self):
        """
        An iterator of all local blocks in the current function.

        :return: angr.lifter.Block instances.
        """

        for block_addr, block in self._local_blocks.items():
            try:
                yield self.get_block(block_addr, size=block.size,
                                      byte_string=block.bytestr if isinstance(block, BlockNode) else None)
            except (SimEngineError, SimMemoryError):
                pass