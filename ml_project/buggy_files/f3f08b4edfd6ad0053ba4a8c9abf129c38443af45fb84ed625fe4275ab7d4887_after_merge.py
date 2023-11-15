    def _poll(self, timeout, sleep=True):
        # select on reads across all connected sockets, blocking up to timeout
        assert self.in_flight_request_count() > 0 or self._connecting or sleep

        responses = []
        processed = set()

        start_select = time.time()
        ready = self._selector.select(timeout)
        end_select = time.time()
        if self._sensors:
            self._sensors.select_time.record((end_select - start_select) * 1000000000)

        for key, events in ready:
            if key.fileobj is self._wake_r:
                self._clear_wake_fd()
                continue
            elif not (events & selectors.EVENT_READ):
                continue
            conn = key.data
            processed.add(conn)

            if not conn.in_flight_requests:
                # if we got an EVENT_READ but there were no in-flight requests, one of
                # two things has happened:
                #
                # 1. The remote end closed the connection (because it died, or because
                #    a firewall timed out, or whatever)
                # 2. The protocol is out of sync.
                #
                # either way, we can no longer safely use this connection
                #
                # Do a 1-byte read to check protocol didnt get out of sync, and then close the conn
                try:
                    unexpected_data = key.fileobj.recv(1)
                    if unexpected_data:  # anything other than a 0-byte read means protocol issues
                        log.warning('Protocol out of sync on %r, closing', conn)
                except socket.error:
                    pass
                conn.close()
                continue

            # Accumulate as many responses as the connection has pending
            while conn.in_flight_requests:
                response = conn.recv() # Note: conn.recv runs callbacks / errbacks

                # Incomplete responses are buffered internally
                # while conn.in_flight_requests retains the request
                if not response:
                    break
                responses.append(response)

        # Check for additional pending SSL bytes
        if self.config['security_protocol'] in ('SSL', 'SASL_SSL'):
            # TODO: optimize
            for conn in self._conns.values():
                if conn not in processed and conn.connected() and conn._sock.pending():
                    response = conn.recv()
                    if response:
                        responses.append(response)

        if self._sensors:
            self._sensors.io_time.record((time.time() - end_select) * 1000000000)
        return responses