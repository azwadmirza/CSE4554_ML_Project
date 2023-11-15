    def create_transfer_block(self, peer, quantity):
        transaction = {"up": 0, "down": int(quantity * MEGA_DIV)}
        self.trustchain.sign_block(peer, peer.public_key.key_to_bin(),
                                   block_type='tribler_bandwidth', transaction=transaction)
        latest_block = self.trustchain.persistence.get_latest(self.trustchain.my_peer.public_key.key_to_bin(),
                                                              block_type='tribler_bandwidth')
        txid = "%s.%s.%d.%d" % (latest_block.public_key.encode('hex'),
                                latest_block.sequence_number, 0, int(quantity * MEGA_DIV))

        self.transaction_history.append({
            'id': txid,
            'outgoing': True,
            'from': self.get_address(),
            'to': b64encode(peer.public_key.key_to_bin()),
            'amount': quantity,
            'fee_amount': 0.0,
            'currency': self.get_identifier(),
            'timestamp': '',
            'description': ''
        })

        return succeed(txid)