    def _create_ssl_context(self,
                            method=SSL_DEFAULT_METHOD,
                            options=SSL_DEFAULT_OPTIONS,
                            verify_options=SSL.VERIFY_NONE,
                            ca_path=None,
                            ca_pemfile=None,
                            cipher_list=None,
                            alpn_protos=None,
                            alpn_select=None,
                            alpn_select_callback=None,
                            sni=None,
                            ):
        """
        Creates an SSL Context.

        :param method: One of SSLv2_METHOD, SSLv3_METHOD, SSLv23_METHOD, TLSv1_METHOD, TLSv1_1_METHOD, or TLSv1_2_METHOD
        :param options: A bit field consisting of OpenSSL.SSL.OP_* values
        :param verify_options: A bit field consisting of OpenSSL.SSL.VERIFY_* values
        :param ca_path: Path to a directory of trusted CA certificates prepared using the c_rehash tool
        :param ca_pemfile: Path to a PEM formatted trusted CA certificate
        :param cipher_list: A textual OpenSSL cipher list, see https://www.openssl.org/docs/apps/ciphers.html
        :rtype : SSL.Context
        """
        try:
            context = SSL.Context(method)
        except ValueError as e:
            method_name = ssl_method_names.get(method, "unknown")
            raise exceptions.TlsException(
                "SSL method \"%s\" is most likely not supported "
                "or disabled (for security reasons) in your libssl. "
                "Please refer to https://github.com/mitmproxy/mitmproxy/issues/1101 "
                "for more details." % method_name
            )

        # Options (NO_SSLv2/3)
        if options is not None:
            context.set_options(options)

        # Verify Options (NONE/PEER and trusted CAs)
        if verify_options is not None:
            def verify_cert(conn, x509, errno, err_depth, is_cert_verified):
                if not is_cert_verified:
                    self.ssl_verification_error = exceptions.InvalidCertificateException(
                        "Certificate Verification Error for {}: {} (errno: {}, depth: {})".format(
                            sni,
                            strutils.native(SSL._ffi.string(SSL._lib.X509_verify_cert_error_string(errno)), "utf8"),
                            errno,
                            err_depth
                        )
                    )
                return is_cert_verified

            context.set_verify(verify_options, verify_cert)
            if ca_path is None and ca_pemfile is None:
                ca_pemfile = certifi.where()
            context.load_verify_locations(ca_pemfile, ca_path)

        # Workaround for
        # https://github.com/pyca/pyopenssl/issues/190
        # https://github.com/mitmproxy/mitmproxy/issues/472
        # Options already set before are not cleared.
        context.set_mode(SSL._lib.SSL_MODE_AUTO_RETRY)

        # Cipher List
        if cipher_list:
            try:
                context.set_cipher_list(cipher_list)

                # TODO: maybe change this to with newer pyOpenSSL APIs
                context.set_tmp_ecdh(OpenSSL.crypto.get_elliptic_curve('prime256v1'))
            except SSL.Error as v:
                raise exceptions.TlsException("SSL cipher specification error: %s" % str(v))

        # SSLKEYLOGFILE
        if log_ssl_key:
            context.set_info_callback(log_ssl_key)

        if HAS_ALPN:
            if alpn_protos is not None:
                # advertise application layer protocols
                context.set_alpn_protos(alpn_protos)
            elif alpn_select is not None and alpn_select_callback is None:
                # select application layer protocol
                def alpn_select_callback(conn_, options):
                    if alpn_select in options:
                        return bytes(alpn_select)
                    else:  # pragma no cover
                        return options[0]
                context.set_alpn_select_callback(alpn_select_callback)
            elif alpn_select_callback is not None and alpn_select is None:
                context.set_alpn_select_callback(alpn_select_callback)
            elif alpn_select_callback is not None and alpn_select is not None:
                raise exceptions.TlsException("ALPN error: only define alpn_select (string) OR alpn_select_callback (method).")

        return context