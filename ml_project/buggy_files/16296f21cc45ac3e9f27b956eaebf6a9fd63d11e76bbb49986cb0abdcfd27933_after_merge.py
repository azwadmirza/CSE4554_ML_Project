    def _handle_event(self, event: Event) -> CommandGenerator[None]:
        if isinstance(event, ResponseHeaders):
            if self.is_open_for_us(event.stream_id):
                headers = [
                    (b":status", b"%d" % event.response.status_code),
                    *event.response.headers.fields
                ]
                if not event.response.is_http2:
                    headers = normalize_h1_headers(headers, False)

                self.h2_conn.send_headers(
                    event.stream_id,
                    headers,
                )
                yield SendData(self.conn, self.h2_conn.data_to_send())
        else:
            yield from super()._handle_event(event)