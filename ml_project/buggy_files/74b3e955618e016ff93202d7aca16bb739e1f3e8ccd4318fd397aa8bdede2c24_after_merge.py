    def _read_forever(self):
        try:
            while True:
                self._receive_packet(self._read_single())
        except KeyboardInterrupt:
            pass
        except Exception:  # connection reset by peer
            log.exception('Exception while reading packet from site, will not attempt to reconnect! Quitting judge.')
            # TODO(tbrindus): this is really sad. This isn't equivalent to `raise SystemExit(1)` since we're not on the
            # main thread, and doing the latter would only exit the network thread. We should fix mid-grading reconnects
            # so that we don't need this sledgehammer approach that relies on Docker restarting the judge for us.
            os._exit(1)