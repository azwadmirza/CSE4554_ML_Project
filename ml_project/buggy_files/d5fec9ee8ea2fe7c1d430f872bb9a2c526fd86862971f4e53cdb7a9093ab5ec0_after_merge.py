    def from_half_block(cls, block, circuit_id):
        return cls(
            circuit_id,
            block.public_key,
            block.sequence_number,
            block.link_public_key,
            block.link_sequence_number,
            block.previous_hash,
            block.signature,
            block.type,
            block._transaction,
            block.timestamp
        )