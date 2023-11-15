    def __init__(self, circuit_id, public_key, sequence_number, link_public_key, link_sequence_number, previous_hash,
                 signature, block_type, transaction, timestamp):
        super(BalanceResponsePayload, self).__init__(public_key, sequence_number, link_public_key,
                                                     link_sequence_number, previous_hash, signature, block_type,
                                                     transaction, timestamp)
        self.circuit_id = circuit_id