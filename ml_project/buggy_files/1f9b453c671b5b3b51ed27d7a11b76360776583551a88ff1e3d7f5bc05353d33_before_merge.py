    def get_current_block_height(self):
        return self.rpc("getblockcount", [])