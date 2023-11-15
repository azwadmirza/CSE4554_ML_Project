    def _cleanup(self) -> None:
        """Cleanup unused transports."""
        if self._cleanup_handle:
            self._cleanup_handle.cancel()

        now = self._loop.time()
        timeout = self._keepalive_timeout

        if self._conns:
            connections = {}
            deadline = now - timeout
            for key, conns in self._conns.items():
                alive = []
                for proto, use_time in conns:
                    if proto.is_connected():
                        if use_time - deadline < 0:
                            transport = proto.transport
                            proto.close()
                            if (key.is_ssl and
                                    not self._cleanup_closed_disabled):
                                self._cleanup_closed_transports.append(
                                    transport)
                        else:
                            alive.append((proto, use_time))

                if alive:
                    connections[key] = alive

            self._conns = connections

        if self._conns:
            self._cleanup_handle = helpers.weakref_handle(
                self, '_cleanup', timeout, self._loop)