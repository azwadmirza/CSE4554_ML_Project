    def ping(self, payload: Union[str, bytes] = "") -> None:
        if self.trace_enabled and self.ping_pong_trace_enabled:
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            self.logger.debug(
                "Sending a ping data frame "
                f"(session id: {self.session_id}, payload: {payload})"
            )
        data = _build_data_frame_for_sending(payload, FrameHeader.OPCODE_PING)
        with self.sock_send_lock:
            self.sock.send(data)