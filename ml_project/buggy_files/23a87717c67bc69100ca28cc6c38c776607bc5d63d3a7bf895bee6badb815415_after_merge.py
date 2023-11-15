    def on_balance_response_cell(self, source_address, payload, _):
        block = TriblerBandwidthBlock.from_payload(payload, self.serializer)
        if not block.transaction:
            self.on_token_balance(payload.circuit_id, 0)
        else:
            self.on_token_balance(payload.circuit_id,
                                  block.transaction[b"total_up"] - block.transaction[b"total_down"])