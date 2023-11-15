    def _read_forever(self):
        try:
            while True:
                self._receive_packet(self._read_single())
        except KeyboardInterrupt:
            pass
        except Exception:  # connection reset by peer
            log.exception('Exception while reading packet from site, will not attempt to reconnect! Quitting judge.')
            raise SystemExit(1)