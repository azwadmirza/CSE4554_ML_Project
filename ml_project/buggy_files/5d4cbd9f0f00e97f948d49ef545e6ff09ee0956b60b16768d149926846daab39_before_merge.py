    def outgoing_request(self, request_id: int, method: str, params: Any, blocking: bool) -> None:
        if not self.settings.log_debug:
            return
        direction = Direction.OutgoingBlocking if blocking else Direction.Outgoing
        self.log(self.format_request(direction, method, request_id), params, self.settings.log_payloads)