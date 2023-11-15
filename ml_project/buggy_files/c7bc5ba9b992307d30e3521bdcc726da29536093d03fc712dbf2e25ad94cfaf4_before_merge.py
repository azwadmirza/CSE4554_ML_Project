    async def send(self, message):
        global DEFAULT_HEADERS

        protocol = self.protocol
        message_type = message["type"]

        if not protocol.writable:
            await protocol.writable_event.wait()

        if not self.response_started:
            # Sending response status line and headers
            if message_type != "http.response.start":
                msg = "Expected ASGI message 'http.response.start', but got '%s'."
                raise RuntimeError(msg % message_type)

            self.response_started = True

            status_code = message["status"]
            headers = DEFAULT_HEADERS + message.get("headers", [])

            if protocol.access_logs:
                protocol.logger.info(
                    '%s - "%s %s HTTP/%s" %d',
                    self.scope["server"][0],
                    self.scope["method"],
                    self.scope["path"],
                    self.scope["http_version"],
                    status_code,
                )

            # Write response status line and headers
            reason = STATUS_PHRASES[status_code]
            event = h11.Response(
                status_code=status_code, headers=headers, reason=reason
            )
            output = protocol.conn.send(event)
            protocol.transport.write(output)

        elif not self.response_complete:
            # Sending response body
            if message_type != "http.response.body":
                msg = "Expected ASGI message 'http.response.body', but got '%s'."
                raise RuntimeError(msg % message_type)

            body = message.get("body", b"")
            more_body = message.get("more_body", False)

            # Write response body
            event = h11.Data(data=body)
            output = protocol.conn.send(event)
            protocol.transport.write(output)

            # Handle response completion
            if not more_body:
                self.response_complete = True
                event = h11.EndOfMessage()
                output = protocol.conn.send(event)
                protocol.transport.write(output)

        else:
            # Response already sent
            msg = "Unexpected ASGI message '%s' sent, after response already completed."
            raise RuntimeError(msg % message_type)

        if protocol.conn.our_state is h11.MUST_CLOSE:
            event = h11.ConnectionClosed()
            protocol.conn.send(event)
            protocol.transport.close()
        elif (
            protocol.conn.our_state is h11.DONE
            and protocol.conn.their_state is h11.DONE
        ):
            protocol.resume_reading()
            protocol.conn.start_next_cycle()