    def on_relay_balance_request_cell(self, source_address, payload, _):
        self.on_balance_request(payload)