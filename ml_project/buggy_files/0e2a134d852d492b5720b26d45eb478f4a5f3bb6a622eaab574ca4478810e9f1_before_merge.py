        def on_nodes(nodes):
            self.logger.debug("Received %d nodes for DHT lookup", len(nodes))
            if nodes:
                self.bandwidth_wallet.trustchain.sign_block(nodes[0],
                                                            public_key=nodes[0].public_key.key_to_bin(),
                                                            block_type='tribler_bandwidth',
                                                            transaction={'up': 0, 'down': total_bytes})