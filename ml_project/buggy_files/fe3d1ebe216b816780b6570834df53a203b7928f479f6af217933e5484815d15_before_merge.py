    def _handle_event(self, event: Event) -> CommandGenerator[None]:
        if isinstance(event, Start):
            self.h2_conn.initiate_connection()
            yield SendData(self.conn, self.h2_conn.data_to_send())

        elif isinstance(event, HttpEvent):
            if isinstance(event, self.SendData):
                assert isinstance(event, (RequestData, ResponseData))
                self.h2_conn.send_data(event.stream_id, event.data)
            elif isinstance(event, self.SendEndOfMessage):
                stream = self.h2_conn.streams.get(event.stream_id)
                if stream.state_machine.state not in (h2.stream.StreamState.HALF_CLOSED_LOCAL,
                                                      h2.stream.StreamState.CLOSED):
                    self.h2_conn.end_stream(event.stream_id)
                if self.is_closed(event.stream_id):
                    self.streams.pop(event.stream_id, None)
            elif isinstance(event, self.SendProtocolError):
                assert isinstance(event, (RequestProtocolError, ResponseProtocolError))
                stream = self.h2_conn.streams.get(event.stream_id)
                if stream.state_machine.state is not h2.stream.StreamState.CLOSED:
                    code = {
                        status_codes.CLIENT_CLOSED_REQUEST: h2.errors.ErrorCodes.CANCEL,
                    }.get(event.code, h2.errors.ErrorCodes.INTERNAL_ERROR)
                    self.h2_conn.reset_stream(event.stream_id, code)
                if self.is_closed(event.stream_id):
                    self.streams.pop(event.stream_id, None)
            else:
                raise AssertionError(f"Unexpected event: {event}")
            data_to_send = self.h2_conn.data_to_send()
            if data_to_send:
                yield SendData(self.conn, data_to_send)

        elif isinstance(event, DataReceived):
            try:
                try:
                    events = self.h2_conn.receive_data(event.data)
                except ValueError as e:  # pragma: no cover
                    # this should never raise a ValueError, but we triggered one while fuzzing:
                    # https://github.com/python-hyper/hyper-h2/issues/1231
                    # this stays here as defense-in-depth.
                    raise h2.exceptions.ProtocolError(f"uncaught hyper-h2 error: {e}") from e
            except h2.exceptions.ProtocolError as e:
                events = [e]

            for h2_event in events:
                if self.debug:
                    yield Log(f"{self.debug}[h2] {h2_event}", "debug")
                if (yield from self.handle_h2_event(h2_event)):
                    if self.debug:
                        yield Log(f"{self.debug}[h2] done", "debug")
                    return

            data_to_send = self.h2_conn.data_to_send()
            if data_to_send:
                yield SendData(self.conn, data_to_send)

        elif isinstance(event, ConnectionClosed):
            yield from self.close_connection("peer closed connection")
        else:
            raise AssertionError(f"Unexpected event: {event!r}")