    def on_relay_balance_response_cell(self, source_address, data, _):
        payload = self._ez_unpack_noauth(BalanceResponsePayload, data, global_time=False)
        block = TriblerBandwidthBlock.from_payload(payload, self.serializer)

        # At this point, we don't have the circuit ID of the follow-up hop. We have to iterate over the items in the
        # request cache and find the link to the next hop.
        for cache in self.request_cache._identifiers.values():
            if isinstance(cache, CreateRequestCache) and cache.from_circuit_id == payload.circuit_id:
                self.send_cell(cache.to_peer,
                               "balance-response",
                               BalanceResponsePayload.from_half_block(block, cache.to_circuit_id))