    def send_request(self, message):
        if self.pushed:
            # nothing to do here
            return

        while True:
            if self.zombie:  # pragma: no cover
                raise exceptions.Http2ProtocolException("Zombie Stream")

            self.server_conn.h2.lock.acquire()

            max_streams = self.server_conn.h2.remote_settings.max_concurrent_streams
            if self.server_conn.h2.open_outbound_streams + 1 >= max_streams:
                # wait until we get a free slot for a new outgoing stream
                self.server_conn.h2.lock.release()
                time.sleep(0.1)
                continue

            # keep the lock
            break

        # We must not assign a stream id if we are already a zombie.
        if self.zombie:  # pragma: no cover
            raise exceptions.Http2ProtocolException("Zombie Stream")

        self.server_stream_id = self.server_conn.h2.get_next_available_stream_id()
        self.server_to_client_stream_ids[self.server_stream_id] = self.client_stream_id

        headers = message.headers.copy()
        headers.insert(0, ":path", message.path)
        headers.insert(0, ":method", message.method)
        headers.insert(0, ":scheme", message.scheme)

        try:
            self.server_conn.h2.safe_send_headers(
                self.is_zombie,
                self.server_stream_id,
                headers,
                end_stream=self.no_body,
                priority_weight=self.priority_weight,
                priority_depends_on=self._map_depends_on_stream_id(self.server_stream_id, self.priority_depends_on),
                priority_exclusive=self.priority_exclusive,
            )
        except Exception as e:
            raise e
        finally:
            self.server_conn.h2.lock.release()

        if not self.no_body:
            self.server_conn.h2.safe_send_body(
                self.is_zombie,
                self.server_stream_id,
                [message.body]
            )

        if self.zombie:  # pragma: no cover
            raise exceptions.Http2ProtocolException("Zombie Stream")