    def on_balance_request(self, payload):
        """
        We received a balance request from a relay or exit node. Respond with the latest block in our chain.
        """
        if not self.bandwidth_wallet:
            self.logger.warning("Bandwidth wallet is not available, not sending balance response!")
            return

        # Get the latest block
        latest_block = self.bandwidth_wallet.trustchain.persistence.get_latest(self.my_peer.public_key.key_to_bin(),
                                                                               block_type=b'tribler_bandwidth')
        if not latest_block:
            latest_block = TriblerBandwidthBlock()
        latest_block.public_key = EMPTY_PK  # We hide the public key

        # We either send the response directly or relay the response to the last verified hop
        circuit = self.circuits[payload.circuit_id]
        if not circuit.hops:
            self.send_cell(circuit.peer, BalanceResponsePayload.from_half_block(latest_block, circuit.circuit_id))
        else:
            self.send_cell(circuit.peer, RelayBalanceResponsePayload.from_half_block(latest_block, circuit.circuit_id))