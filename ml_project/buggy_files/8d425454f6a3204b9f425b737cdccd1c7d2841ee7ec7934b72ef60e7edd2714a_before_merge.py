    def tls_session_update(self, msg_str):
        """
        Either for parsing or building, we store the client_random
        along with the raw string representing this handshake message.
        """
        super(TLS13ClientHello, self).tls_session_update(msg_str)
        s = self.tls_session

        if self.sidlen and self.sidlen > 0:
            s.sid = self.sid
            s.middlebox_compatibility = True

        self.random_bytes = msg_str[10:38]
        s.client_random = self.random_bytes
        if self.ext:
            for e in self.ext:
                if isinstance(e, TLS_Ext_SupportedVersion_CH):
                    for ver in e.versions:
                        # RFC 8701: GREASE of TLS will send unknown versions
                        # here. We have to ignore them
                        if ver in _tls_version:
                            self.tls_session.advertised_tls_version = ver
                            break
                if isinstance(e, TLS_Ext_SignatureAlgorithms):
                    s.advertised_sig_algs = e.sig_algs