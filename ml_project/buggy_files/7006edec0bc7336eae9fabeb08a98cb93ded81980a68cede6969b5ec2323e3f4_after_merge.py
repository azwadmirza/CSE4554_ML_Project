    def request_or_notification_handler(self, payload: Mapping[str, Any]) -> None:
        method = payload["method"]  # type: str
        params = payload.get("params")
        # Server request IDs can be either a string or an int.
        request_id = payload.get("id")
        if request_id is not None:
            self.handle(request_id, method, params, "request", self._request_handlers,
                        lambda *args: self.logger.incoming_request(request_id, *args))
        else:
            self.handle(None, method, params, "notification", self._notification_handlers,
                        self.logger.incoming_notification)