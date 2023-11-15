    def _establish_tls_with_server(self):
        self.log("Establish TLS with server", "debug")
        try:
            # We only support http/1.1 and h2.
            # If the server only supports spdy (next to http/1.1), it may select that
            # and mitmproxy would enter TCP passthrough mode, which we want to avoid.
            def deprecated_http2_variant(x):
                return x.startswith(b"h2-") or x.startswith(b"spdy")

            if self._client_hello.alpn_protocols:
                alpn = [x for x in self._client_hello.alpn_protocols if not deprecated_http2_variant(x)]
            else:
                alpn = None
            if alpn and b"h2" in alpn and not self.config.options.http2:
                alpn.remove(b"h2")

            ciphers_server = self.config.options.ciphers_server
            if not ciphers_server:
                ciphers_server = []
                for id in self._client_hello.cipher_suites:
                    if id in CIPHER_ID_NAME_MAP.keys():
                        ciphers_server.append(CIPHER_ID_NAME_MAP[id])
                ciphers_server = ':'.join(ciphers_server)

            self.server_conn.establish_ssl(
                self.config.clientcerts,
                self.server_sni,
                method=self.config.openssl_method_server,
                options=self.config.openssl_options_server,
                verify_options=self.config.openssl_verification_mode_server,
                ca_path=self.config.options.ssl_verify_upstream_trusted_cadir,
                ca_pemfile=self.config.options.ssl_verify_upstream_trusted_ca,
                cipher_list=ciphers_server,
                alpn_protos=alpn,
            )
            tls_cert_err = self.server_conn.ssl_verification_error
            if tls_cert_err is not None:
                self.log(str(tls_cert_err), "warn")
                self.log("Ignoring server verification error, continuing with connection", "warn")
        except netlib.exceptions.InvalidCertificateException as e:
            six.reraise(
                exceptions.InvalidServerCertificate,
                exceptions.InvalidServerCertificate(str(e)),
                sys.exc_info()[2]
            )
        except netlib.exceptions.TlsException as e:
            six.reraise(
                exceptions.TlsProtocolException,
                exceptions.TlsProtocolException("Cannot establish TLS with {address} (sni: {sni}): {e}".format(
                    address=repr(self.server_conn.address),
                    sni=self.server_sni,
                    e=repr(e),
                )),
                sys.exc_info()[2]
            )

        self.log("ALPN selected by server: %s" % self.alpn_for_client_connection, "debug")