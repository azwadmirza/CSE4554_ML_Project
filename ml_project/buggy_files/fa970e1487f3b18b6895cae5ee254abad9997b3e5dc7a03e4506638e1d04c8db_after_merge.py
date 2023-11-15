    def tls_session_update(self, msg_str):
        """
        Either for parsing or building, we store the server_random
        along with the raw string representing this handshake message.
        We also store the session_id, the cipher suite (if recognized),
        the compression method, and finally we instantiate the pending write
        and read connection states. Usually they get updated later on in the
        negotiation when we learn the session keys, and eventually they
        are committed once a ChangeCipherSpec has been sent/received.
        """
        super(TLSServerHello, self).tls_session_update(msg_str)

        s = self.tls_session
        s.tls_version = self.version
        if hasattr(self, 'gmt_unix_time'):
            self.random_bytes = msg_str[10:38]
            s.server_random = (struct.pack('!I', self.gmt_unix_time) +
                               self.random_bytes)
        else:
            s.server_random = self.random_bytes
        s.sid = self.sid

        cs_cls = None
        if self.cipher:
            cs_val = self.cipher
            if cs_val not in _tls_cipher_suites_cls:
                warning("Unknown cipher suite %d from ServerHello" % cs_val)
                # we do not try to set a default nor stop the execution
            else:
                cs_cls = _tls_cipher_suites_cls[cs_val]

        comp_cls = Comp_NULL
        if self.comp:
            comp_val = self.comp[0]
            if comp_val not in _tls_compression_algs_cls:
                err = "Unknown compression alg %d from ServerHello" % comp_val
                warning(err)
                comp_val = 0
            comp_cls = _tls_compression_algs_cls[comp_val]

        connection_end = s.connection_end
        s.pwcs = writeConnState(ciphersuite=cs_cls,
                                compression_alg=comp_cls,
                                connection_end=connection_end,
                                tls_version=self.version)
        s.prcs = readConnState(ciphersuite=cs_cls,
                               compression_alg=comp_cls,
                               connection_end=connection_end,
                               tls_version=self.version)