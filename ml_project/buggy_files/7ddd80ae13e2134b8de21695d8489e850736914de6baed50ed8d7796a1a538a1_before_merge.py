    def data_received(self, data):
        if self._force_close or self._close:
            return

        # parse http messages
        if self._payload_parser is None and not self._upgrade:
            try:
                messages, upgraded, tail = self._request_parser.feed_data(data)
            except HttpProcessingError as exc:
                # something happened during parsing
                self._error_handler = self._loop.create_task(
                    self.handle_parse_error(
                        StreamWriter(self, self.transport, self._loop),
                        400, exc, exc.message))
                self.close()
            except Exception as exc:
                # 500: internal error
                self._error_handler = self._loop.create_task(
                    self.handle_parse_error(
                        StreamWriter(self, self.transport, self._loop),
                        500, exc))
                self.close()
            else:
                for (msg, payload) in messages:
                    self._request_count += 1
                    self._messages.append((msg, payload))

                if self._waiter:
                    self._waiter.set_result(None)

                self._upgraded = upgraded
                if upgraded and tail:
                    self._message_tail = tail

        # no parser, just store
        elif self._payload_parser is None and self._upgrade and data:
            self._message_tail += data

        # feed payload
        elif data:
            eof, tail = self._payload_parser.feed_data(data)
            if eof:
                self.close()