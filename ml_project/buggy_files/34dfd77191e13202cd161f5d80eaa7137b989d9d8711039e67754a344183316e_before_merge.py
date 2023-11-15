    def incoming_notification(self, method: str, params: Any, unhandled: bool) -> None:
        if not self.settings.log_debug or method == "window/logMessage":
            return
        direction = "unhandled" if unhandled else Direction.Incoming
        self.log(self.format_notification(direction, method), params, self.settings.log_payloads)