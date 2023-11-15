    def run_until_completion(self, state: ConnectionState) -> None:
        repeated_messages = {"payload": 0}
        ping_count = 0
        pong_count = 0
        ping_pong_log_summary_size = 1000
        while not state.terminated:
            try:
                if self.is_active():
                    received_messages: List[
                        Tuple[Optional[FrameHeader], bytes]
                    ] = _receive_messages(
                        sock=self.sock,
                        logger=self.logger,
                        receive_buffer_size=self.receive_buffer_size,
                        all_message_trace_enabled=self.all_message_trace_enabled,
                    )
                    for message in received_messages:
                        header, data = message

                        # -----------------
                        # trace logging

                        if self.trace_enabled is True:
                            opcode: str = (
                                _to_readable_opcode(header.opcode) if header else "-"
                            )
                            payload: str = _parse_text_payload(data, self.logger)
                            count: Optional[int] = repeated_messages.get(payload)
                            if count is None:
                                count = 1
                            else:
                                count += 1
                            repeated_messages = {payload: count}
                            if (
                                not self.ping_pong_trace_enabled
                                and header is not None
                                and header.opcode is not None
                            ):
                                if header.opcode == FrameHeader.OPCODE_PING:
                                    ping_count += 1
                                    if ping_count % ping_pong_log_summary_size == 0:
                                        self.logger.debug(
                                            f"Received {ping_pong_log_summary_size} ping data frame "
                                            f"(session id: {self.session_id})"
                                        )
                                        ping_count = 0
                                if header.opcode == FrameHeader.OPCODE_PONG:
                                    pong_count += 1
                                    if pong_count % ping_pong_log_summary_size == 0:
                                        self.logger.debug(
                                            f"Received {ping_pong_log_summary_size} pong data frame "
                                            f"(session id: {self.session_id})"
                                        )
                                        pong_count = 0

                            ping_pong_to_skip = (
                                header is not None
                                and header.opcode is not None
                                and (
                                    header.opcode == FrameHeader.OPCODE_PING
                                    or header.opcode == FrameHeader.OPCODE_PONG
                                )
                                and not self.ping_pong_trace_enabled
                            )
                            if not ping_pong_to_skip and count < 5:
                                # if so many same payloads came in, the trace logging should be skipped.
                                # e.g., after receiving "UNAUTHENTICATED: cache_error", many "opcode: -, payload: "
                                self.logger.debug(
                                    "Received a new data frame "
                                    f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                                )

                        if header is None:
                            # Skip no header message
                            continue

                        # -----------------
                        # message with opcode

                        if header.opcode == FrameHeader.OPCODE_PING:
                            self.pong(data)
                        elif header.opcode == FrameHeader.OPCODE_PONG:
                            str_message = data.decode("utf-8")
                            elements = str_message.split(":")
                            if len(elements) >= 2:
                                session_id, ping_time = elements[0], elements[1]
                                if self.session_id == session_id:
                                    try:
                                        self.last_ping_pong_time = float(ping_time)
                                    except Exception as e:
                                        self.logger.debug(
                                            "Failed to parse a pong message "
                                            f" (message: {str_message}, error: {e}"
                                        )
                        elif header.opcode == FrameHeader.OPCODE_TEXT:
                            if self.on_message_listener is not None:
                                text = data.decode("utf-8")
                                self.on_message_listener(text)
                        elif header.opcode == FrameHeader.OPCODE_CLOSE:
                            if self.on_close_listener is not None:
                                if len(data) >= 2:
                                    (code,) = struct.unpack("!H", data[:2])
                                    reason = data[2:].decode("utf-8")
                                    self.on_close_listener(code, reason)
                                else:
                                    self.on_close_listener(1005, "")
                            self.disconnect()
                            state.terminated = True
                        else:
                            # Just warn logging
                            opcode = (
                                _to_readable_opcode(header.opcode) if header else "-"
                            )
                            payload: Union[bytes, str] = data
                            if header.opcode != FrameHeader.OPCODE_BINARY:
                                try:
                                    payload = (
                                        data.decode("utf-8") if data is not None else ""
                                    )
                                except Exception as e:
                                    self.logger.info(
                                        f"Failed to convert the data to text {e}"
                                    )
                            message = (
                                "Received an unsupported data frame "
                                f"(session id: {self.session_id}, opcode: {opcode}, payload: {payload})"
                            )
                            self.logger.warning(message)
                else:
                    time.sleep(0.2)
            except socket.timeout:
                time.sleep(0.01)
            except OSError as e:
                # getting errno.EBADF and the socket is no longer available
                if e.errno == 9 and state.terminated:
                    self.logger.debug(
                        "The reason why you got [Errno 9] Bad file descriptor here is "
                        "the socket is no longer available."
                    )
                else:
                    if self.on_error_listener is not None:
                        self.on_error_listener(e)
                    else:
                        self.logger.exception(
                            "Got an OSError while receiving data"
                            f" (session id: {self.session_id}, error: {e})"
                        )
                # As this connection no longer works in any way, terminating it
                if self.is_active():
                    try:
                        self.disconnect()
                    except Exception as disconnection_error:
                        self.logger.exception(
                            "Failed to disconnect"
                            f" (session id: {self.session_id}, error: {disconnection_error})"
                        )
                state.terminated = True
                break
            except Exception as e:
                if self.on_error_listener is not None:
                    self.on_error_listener(e)
                else:
                    self.logger.exception(
                        "Got an exception while receiving data"
                        f" (session id: {self.session_id}, error: {e})"
                    )

        state.terminated = True