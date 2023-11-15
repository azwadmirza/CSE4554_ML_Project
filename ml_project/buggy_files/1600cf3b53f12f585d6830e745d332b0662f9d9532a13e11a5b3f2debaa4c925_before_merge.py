    def send(self, payload: str) -> None:
        if self.trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a text data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_TEXT)
        self.sock.send(data)