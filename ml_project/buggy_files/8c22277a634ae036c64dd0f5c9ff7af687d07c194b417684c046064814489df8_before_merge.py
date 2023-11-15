    def on_balance_request_cell(self, source_address, data, _):
        payload = self._ez_unpack_noauth(BalanceRequestPayload, data, global_time=False)

        if self.request_cache.has(u"create", payload.circuit_id):
            request = self.request_cache.get(u"create", payload.circuit_id)
            forwarding_relay = RelayRoute(request.from_circuit_id, request.peer)
            self.send_cell(forwarding_relay.peer, u"relay-balance-request",
                           BalanceRequestPayload(forwarding_relay.circuit_id))
        elif self.request_cache.has(u"retry", payload.circuit_id):
            self.on_balance_request(payload)
        else:
            self.logger.warning("Circuit creation cache for id %s not found!", payload.circuit_id)