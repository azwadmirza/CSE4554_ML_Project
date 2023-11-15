    def run(self):
        lh = self.network.get_local_height()
        unverified = self.wallet.get_unverified_txs()
        for tx_hash, tx_height in unverified.items():
            # do not request merkle branch before headers are available
            if (tx_height > 0) and (tx_height <= lh):
                header = self.network.blockchain().read_header(tx_height)
                index = tx_height // 2016
                #print(index, header)
                if header is None:
                    if index not in self.requested_chunks  and self.network.interface:
                        print("requesting chunk", index)
                        #request = ('blockchain.block.get_chunk', [index])
                        #self.network.send([request], self.verify_merkle)
                        self.requested_chunks[index] = None
                        self.network.request_chunk(self.network.interface, index)
                else:
                    if tx_hash not in self.merkle_roots:
                        request = ('blockchain.transaction.get_merkle',
                                   [tx_hash, tx_height])
                        self.network.send([request], self.verify_merkle)
                        self.print_error('requested merkle', tx_hash)
                        self.merkle_roots[tx_hash] = None

        if self.network.blockchain() != self.blockchain:
            self.blockchain = self.network.blockchain()
            self.undo_verifications()