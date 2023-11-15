        def _identityVerifyingInfoCallback(self, connection, where, ret):
            if where & SSL_CB_HANDSHAKE_START:
                _maybeSetHostNameIndication(connection, self._hostnameBytes)
            elif where & SSL_CB_HANDSHAKE_DONE:
                try:
                    verifyHostname(connection, self._hostnameASCII)
                except VerificationError as e:
                    logger.warning(
                        'Remote certificate is not valid for hostname "{}"; {}'.format(
                            self._hostnameASCII, e))

                except ValueError as e:
                    logger.warning(
                        'Ignoring error while verifying certificate '
                        'from host "{}" (exception: {})'.format(
                            self._hostnameASCII, repr(e)))