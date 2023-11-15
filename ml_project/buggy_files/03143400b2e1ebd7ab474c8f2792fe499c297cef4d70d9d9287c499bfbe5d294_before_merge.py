    def m2i(self, pkt, m):
        """
        Try to parse one of the TLS subprotocols (ccs, alert, handshake or
        application_data). This is used inside a loop managed by .getfield().
        """
        cls = Raw
        if pkt.type == 22:
            if len(m) >= 1:
                msgtype = orb(m[0])
                if ((pkt.tls_session.advertised_tls_version == 0x0304) or
                        (pkt.tls_session.tls_version and
                         pkt.tls_session.tls_version == 0x0304)):
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