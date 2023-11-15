    def tls_session_update(self, msg_str):
        """
        Either for parsing or building, we store the server_random along with
        the raw string representing this handshake message. We also store the
        cipher suite (if recognized), and finally we instantiate the write and
        read connection states.
        """
        s = self.tls_session
        s.server_random = self.random_bytes
        s.ciphersuite = self.cipher
        s.tls_version = self.version
        # Check extensions
        if self.ext:
            for e in self.ext:
                if isinstance(e, TLS_Ext_SupportedVersion_SH):
                    s.tls_version = e.version
                    break

        if s.tls_version < 0x304:
            # This means that the server does not support TLS 1.3 and ignored
            # the initial TLS 1.3 ClientHello. tls_version has been updated
            return TLSServerHello.tls_session_update(self, msg_str)
        else:
            _TLSHandshake.tls_session_update(self, msg_str)

        cs_cls = None
        if self.cipher:
            cs_val = self.cipher
            if cs_val not in _tls_cipher_suites_cls:
                warning("Unknown cipher suite %d from ServerHello" % cs_val)
                # we do not try to set a default nor stop the execution
            else:
                cs_cls = _tls_cipher_suites_cls[cs_val]

        connection_end = s.connection_end
        if connection_end == "server":
            s.pwcs = writeConnState(ciphersuite=cs_cls,
                                    connection_end=connection_end,
                                    tls_version=s.tls_version)

            if not s.middlebox_compatibility:
                s.triggered_pwcs_commit = True
        elif connection_end == "client":

            s.prcs = readConnState(ciphersuite=cs_cls,
                                   connection_end=connection_end,
                                   tls_version=s.tls_version)
            if not s.middlebox_compatibility:
                s.triggered_prcs_commit = True

        if s.tls13_early_secret is None:
            # In case the connState was not pre-initialized, we could not
            # compute the early secrets at the ClientHello, so we do it here.
            s.compute_tls13_early_secrets()
        s.compute_tls13_handshake_secrets()
        if connection_end == "server":
            shts = s.tls13_derived_secrets["server_handshake_traffic_secret"]
            s.pwcs.tls13_derive_keys(shts)
        elif connection_end == "client":
            shts = s.tls13_derived_secrets["server_handshake_traffic_secret"]
            s.prcs.tls13_derive_keys(shts)