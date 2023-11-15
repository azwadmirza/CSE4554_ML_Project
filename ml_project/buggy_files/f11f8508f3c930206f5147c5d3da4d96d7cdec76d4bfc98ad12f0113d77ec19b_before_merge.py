    def incoming_response(self, request_id: int, params: Any) -> None:
        if not self.settings.log_debug:
            return
        self.log(self.format_response(Direction.Incoming, request_id), params, self.settings.log_payloads)