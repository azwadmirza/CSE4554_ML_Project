    def get_options(self, host):
        # Check if certificate verification has been enabled
        should_verify = self._config.federation_verify_certificates

        # Check if we've disabled certificate verification for this host
        if should_verify:
            for regex in self._config.federation_certificate_verification_whitelist:
                if regex.match(host):
                    should_verify = False
                    break

        ssl_context = (
            self._verify_ssl_context if should_verify else self._no_verify_ssl_context
        )

        return SSLClientConnectionCreator(host, ssl_context, should_verify)