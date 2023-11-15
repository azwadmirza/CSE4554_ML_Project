    def update_blockheight(self):
        """ Can be called manually (on startup, or for tests)
        but will be called as part of main monitoring
        loop to ensure new transactions are added at
        the right height.
        Any failure of the RPC call must result in this returning
        False, otherwise return True (means self.current_blockheight
        has been correctly updated).
        """

        def critical_error():
            jlog.error("Failure to get blockheight from Bitcoin Core.")
            self.stopService()
            return False

        if self.current_blockheight:
            old_blockheight = self.current_blockheight
        else:
            old_blockheight = -1
        try:
            self.current_blockheight = self.bci.get_current_block_height()
        except Exception as e:
            # This should never happen now, as we are catching every
            # possible Exception in jsonrpc or bci.rpc:
            return critical_error()
        if not self.current_blockheight:
            return critical_error()

        # We have received a new blockheight from Core, sanity check it:
        assert isinstance(self.current_blockheight, Integral)
        assert self.current_blockheight >= 0
        if self.current_blockheight < old_blockheight:
            jlog.warn("Bitcoin Core is reporting a lower blockheight, "
                      "possibly a reorg.")
        return True