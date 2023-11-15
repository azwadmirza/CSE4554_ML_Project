    def incoming_request(self, request_id: Any, method: str, params: Any, unhandled: bool) -> None:
        if not self.settings.log_debug:
            return
        direction = "unhandled" if unhandled else Direction.Incoming
        self.log(self.format_request(direction, method, request_id), params, self.settings.log_payloads)