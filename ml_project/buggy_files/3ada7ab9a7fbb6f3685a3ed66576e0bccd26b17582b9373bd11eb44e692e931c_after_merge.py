    def do_payout(self, mid):
        """
        Perform a payout to a given mid. First, determine the outstanding balance. Then resolve the node in the DHT.
        """
        if mid not in self.tribler_peers:
            return

        total_bytes = 0
        for balance in self.tribler_peers[mid].itervalues():
            total_bytes += balance

        def on_nodes(nodes):
            self.logger.debug("Received %d nodes for DHT lookup", len(nodes))
            if nodes:
                self.bandwidth_wallet.trustchain.sign_block(nodes[0],
                                                            public_key=nodes[0].public_key.key_to_bin(),
                                                            block_type='tribler_bandwidth',
                                                            transaction={'up': 0, 'down': total_bytes})

        if total_bytes >= 1024 * 1024:  # Do at least 1MB payouts
            self.logger.info("Doing direct payout to %s (%d bytes)", mid.encode('hex'), total_bytes)
            self.dht.connect_peer(mid).addCallbacks(on_nodes, lambda _: on_nodes([]))

        # Remove the outstanding bytes; otherwise we will payout again
        self.tribler_peers.pop(mid, None)