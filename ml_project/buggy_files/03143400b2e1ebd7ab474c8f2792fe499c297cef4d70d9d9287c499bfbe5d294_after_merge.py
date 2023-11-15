    def m2i(self, pkt, m):
        """
        Try to parse one of the TLS subprotocols (ccs, alert, handshake or
        application_data). This is used inside a loop managed by .getfield().
        """
        cls = Raw
        if pkt.type == 22:
            if len(m) >= 1:
                msgtype = orb(m[0])
                # If a version was agreed on by both client and server,
                # we use it (tls_session.tls_version)
                # Otherwise, if the client advertised for TLS 1.3, we try to
                # dissect the following packets (most likely, server hello)
                # using TLS 1.3. The serverhello is able to fallback on
                # TLS 1.2 if necessary. In any case, this will set the agreed
                # version so that all future packets are correct.
                if ((pkt.tls_session.advertised_tls_version == 0x0304 and
                        pkt.tls_session.tls_version is None) or
                        pkt.tls_session.tls_version == 0x0304):
                    cls = _tls13_handshake_cls.get(msgtype, Raw)
                else:
                    cls = _tls_handshake_cls.get(msgtype, Raw)

        elif pkt.type == 20:
            cls = TLSChangeCipherSpec
        elif pkt.type == 21:
            cls = TLSAlert
        elif pkt.type == 23:
            cls = TLSApplicationData

        if cls is Raw:
            return Raw(m)
        else:
            try:
                return cls(m, tls_session=pkt.tls_session)
            except Exception:
                if conf.debug_dissector:
                    raise
                return Raw(m)