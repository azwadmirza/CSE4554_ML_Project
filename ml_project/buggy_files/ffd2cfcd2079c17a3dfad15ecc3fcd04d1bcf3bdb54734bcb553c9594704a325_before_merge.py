    def _get(self, key: 'ConnectionKey') -> Optional[ResponseHandler]:
        try:
            conns = self._conns[key]
        except KeyError:
            return None

        t1 = self._loop.time()
        while conns:
            proto, t0 = conns.pop()
            if proto.is_connected():
                if t1 - t0 > self._keepalive_timeout:
                    transport = proto.transport
                    proto.close()
                    # only for SSL transports
                    if key.is_ssl and not self._cleanup_closed_disabled:
                        self._cleanup_closed_transports.append(transport)
                else:
                    if not conns:
                        # The very last connection was reclaimed: drop the key
                        del self._conns[key]
                    return proto

        # No more connections: drop the key
        del self._conns[key]
        return None