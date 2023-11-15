    def _send_packet(self, packet: dict):
        for k, v in packet.items():
            if isinstance(v, bytes):
                # Make sure we don't have any garbage utf-8 from e.g. weird compilers
                # *cough* fpc *cough* that could cause this routine to crash
                # We cannot use utf8text because it may not be text.
                packet[k] = v.decode('utf-8', 'replace')

        raw = zlib.compress(utf8bytes(json.dumps(packet)))
        with self._lock:
            try:
                self.output.writelines((PacketManager.SIZE_PACK.pack(len(raw)), raw))
            except Exception:  # connection reset by peer
                log.exception('Exception while sending packet to site, will not attempt to reconnect! Quitting judge.')
                raise SystemExit(1)