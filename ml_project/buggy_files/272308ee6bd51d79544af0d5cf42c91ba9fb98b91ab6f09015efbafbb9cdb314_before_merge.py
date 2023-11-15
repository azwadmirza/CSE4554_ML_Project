    def build(self, *args, **kargs):
        r"""
        We overload build() method in order to provide a valid default value
        for params based on TLS session if not provided. This cannot be done by
        overriding i2m() because the method is called on a copy of the packet.

        The 'params' field is built according to key_exchange.server_kx_msg_cls
        which should have been set after receiving a cipher suite in a
        previous ServerHello. Usual cases are:

        - None: for RSA encryption or fixed FF/ECDH. This should never happen,
          as no ServerKeyExchange should be generated in the first place.
        - ServerDHParams: for ephemeral FFDH. In that case, the parameter to
          server_kx_msg_cls does not matter.
        - ServerECDH\*Params: for ephemeral ECDH. There are actually three
          classes, which are dispatched by _tls_server_ecdh_cls_guess on
          the first byte retrieved. The default here is b"\03", which
          corresponds to ServerECDHNamedCurveParams (implicit curves).

        When the Server\*DHParams are built via .fill_missing(), the session
        server_kx_privkey will be updated accordingly.
        """
        fval = self.getfieldval("params")
        if fval is None:
            s = self.tls_session
            if s.pwcs:
                if s.pwcs.key_exchange.export:
                    cls = ServerRSAParams(tls_session=s)
                else:
                    cls = s.pwcs.key_exchange.server_kx_msg_cls(b"\x03")
                    cls = cls(tls_session=s)
                try:
                    cls.fill_missing()
                except Exception:
                    if conf.debug_dissector:
                        raise
            else:
                cls = Raw()
            self.params = cls

        fval = self.getfieldval("sig")
        if fval is None:
            s = self.tls_session
            if s.pwcs:
                if not s.pwcs.key_exchange.anonymous:
                    p = self.params
                    if p is None:
                        p = b""
                    m = s.client_random + s.server_random + raw(p)
                    cls = _TLSSignature(tls_session=s)
                    cls._update_sig(m, s.server_key)
                else:
                    cls = Raw()
            else:
                cls = Raw()
            self.sig = cls

        return _TLSHandshake.build(self, *args, **kargs)