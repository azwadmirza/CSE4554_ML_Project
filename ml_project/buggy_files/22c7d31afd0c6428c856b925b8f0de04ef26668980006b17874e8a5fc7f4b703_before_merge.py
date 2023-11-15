    def outgoing_response(self, request_id: Any, params: Any) -> None:
        if not self.settings.log_debug:
            return
        self.log(self.format_response(Direction.Outgoing, request_id), params, self.settings.log_payloads)