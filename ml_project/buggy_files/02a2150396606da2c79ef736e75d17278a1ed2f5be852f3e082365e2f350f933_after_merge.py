    def on_balance_request_cell(self, source_address, data, _):
        payload = self._ez_unpack_noauth(BalanceRequestPayload, data, global_time=False)

        circuit_id = payload.circuit_id
        request = self.request_cache.get(u"anon-circuit", circuit_id)
        if not request:
            self.logger.warning("Circuit creation cache for id %s not found!", circuit_id)
            return

        if request.should_forward:
            forwarding_relay = RelayRoute(request.from_circuit_id, request.peer)
            self.send_cell([forwarding_relay.peer.address], u"relay-balance-request",
                           BalanceRequestPayload(forwarding_relay.circuit_id))
        else:
            self.on_balance_request(payload)