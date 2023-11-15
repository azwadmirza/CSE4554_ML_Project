    def tls_session_update(self, msg_str):
        """
        Either for parsing or building, we store the client_random
        along with the raw string representing this handshake message.
        """
        super(TLSClientHello, self).tls_session_update(msg_str)
        s = self.tls_session
        s.advertised_tls_version = self.version
        # This ClientHello could be a 1.3 one. Let's store the sid
        # in all cases
        if self.sidlen and self.sidlen > 0:
            s.sid = self.sid
        self.random_bytes = msg_str[10:38]
        s.client_random = (struct.pack('!I', self.gmt_unix_time) +
                           self.random_bytes)

        # No distinction between a TLS 1.2 ClientHello and a TLS
        # 1.3 ClientHello when dissecting : TLS 1.3 CH will be
        # parsed as TLSClientHello
        if self.ext:
            for e in self.ext:
                if isinstance(e, TLS_Ext_SupportedVersion_CH):
                    for ver in sorted(e.versions, reverse=True):
                        # RFC 8701: GREASE of TLS will send unknown versions
                        # here. We have to ignore them
                        if ver in _tls_version:
                            s.advertised_tls_version = ver
                            break
                    if s.sid:
                        s.middlebox_compatibility = True

                if isinstance(e, TLS_Ext_SignatureAlgorithms):
                    s.advertised_sig_algs = e.sig_algs