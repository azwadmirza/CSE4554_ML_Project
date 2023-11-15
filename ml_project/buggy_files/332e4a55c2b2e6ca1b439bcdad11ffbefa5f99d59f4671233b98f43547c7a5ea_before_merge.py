    def __call__(self):
        """
        The strategy for establishing TLS is as follows:
            First, we determine whether we need the server cert to establish ssl with the client.
            If so, we first connect to the server and then to the client.
            If not, we only connect to the client and do the server handshake lazily.

        An additional complexity is that we need to mirror SNI and ALPN from the client when connecting to the server.
        We manually peek into the connection and parse the ClientHello message to obtain these values.
        """
        if self._client_tls:
            # Peek into the connection, read the initial client hello and parse it to obtain SNI and ALPN values.
            try:
                self._client_hello = TlsClientHello.from_client_conn(self.client_conn)
            except exceptions.TlsProtocolException as e:
                self.log("Cannot parse Client Hello: %s" % repr(e), "error")

        # Do we need to do a server handshake now?
        # There are two reasons why we would want to establish TLS with the server now:
        #  1. If we already have an existing server connection and server_tls is True,
        #     we need to establish TLS now because .connect() will not be called anymore.
        #  2. We may need information from the server connection for the client handshake.
        #
        # A couple of factors influence (2):
        #  2.1 There actually is (or will be) a TLS-enabled upstream connection
        #  2.2 An upstream connection is not wanted by the user if --no-upstream-cert is passed.
        #  2.3 An upstream connection is implied by add_upstream_certs_to_client_chain
        #  2.4 The client wants to negotiate an alternative protocol in its handshake, we need to find out
        #      what is supported by the server
        #  2.5 The client did not sent a SNI value, we don't know the certificate subject.
        client_tls_requires_server_connection = (
            self._server_tls and
            not self.config.options.no_upstream_cert and
            (
                self.config.options.add_upstream_certs_to_client_chain or
                self._client_hello.alpn_protocols or
                not self._client_hello.sni
            )
        )
        establish_server_tls_now = (
            (self.server_conn and self._server_tls) or
            client_tls_requires_server_connection
        )

        if self._client_tls and establish_server_tls_now:
            self._establish_tls_with_client_and_server()
        elif self._client_tls:
            self._establish_tls_with_client()
        elif establish_server_tls_now:
            self._establish_tls_with_server()

        layer = self.ctx.next_layer(self)
        layer()