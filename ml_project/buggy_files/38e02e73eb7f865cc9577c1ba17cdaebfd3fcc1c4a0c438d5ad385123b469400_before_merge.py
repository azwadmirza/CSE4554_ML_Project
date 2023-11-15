    def outgoing_notification(self, method: str, params: Any) -> None:
        if not self.settings.log_debug:
            return
        # Do not log the payloads if any of these conditions occur because the payloads might contain the entire
        # content of the view.
        log_payload = self.settings.log_payloads \
            and method != "textDocument/didChange" \
            and method != "textDocument/didOpen"
        if log_payload and method == "textDocument/didSave" and isinstance(params, dict) and "text" in params:
            log_payload = False
        self.log(self.format_notification(Direction.Outgoing, method), params, log_payload)