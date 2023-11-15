    def get_options(self, host: bytes):

        # IPolicyForHTTPS.get_options takes bytes, but we want to compare
        # against the str whitelist. The hostnames in the whitelist are already
        # IDNA-encoded like the hosts will be here.
        ascii_host = host.decode("ascii")

        # Check if certificate verification has been enabled
        should_verify = self._config.federation_verify_certificates

        # Check if we've disabled certificate verification for this host
        if should_verify:
            for regex in self._config.federation_certificate_verification_whitelist:
                if regex.match(ascii_host):
                    should_verify = False
                    break

        ssl_context = (
            self._verify_ssl_context if should_verify else self._no_verify_ssl_context
        )

        return SSLClientConnectionCreator(host, ssl_context, should_verify)