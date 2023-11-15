    def _process_block(self, state, block):  #pylint:disable=no-self-use
        """
        Scan through all statements and perform the following tasks:
        - Find stack pointers and the VEX temporary variable storing stack pointers
        - Selectively calculate VEX statements
        - Track memory loading and mark stack and global variables accordingly

        :param angr.Block block:
        :return:
        """

        l.debug('Processing block %#x.', block.addr)

        processor = self._ail_engine if isinstance(block, ailment.Block) else self._vex_engine
        processor.process(state, block=block, fail_fast=self._fail_fast)

        # readjusting sp at the end for blocks that end in a call
        if block.addr in self._node_to_cc:
            cc = self._node_to_cc[block.addr]
            state.processor_state.sp_adjustment += cc.sp_delta
            state.processor_state.sp_adjusted = True
            l.debug('Adjusting stack pointer at end of block %#x with offset %+#x.', block.addr, state.processor_state.sp_adjustment)