    def get_current_block_height(self):
        try:
            res = self.rpc("getblockcount", [])
        except JsonRpcError as e:
            log.error("Getblockcount RPC failed with: %i, %s" % (
                e.code, e.message))
            res = None
        return res