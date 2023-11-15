    def __init__(self, reactor, tls_client_options_factory, srv_resolver, parsed_uri):
        self._reactor = reactor

        self._parsed_uri = parsed_uri

        # set up the TLS connection params
        #
        # XXX disabling TLS is really only supported here for the benefit of the
        # unit tests. We should make the UTs cope with TLS rather than having to make
        # the code support the unit tests.

        if tls_client_options_factory is None:
            self._tls_options = None
        else:
            self._tls_options = tls_client_options_factory.get_options(
                self._parsed_uri.host.decode("ascii")
            )

        self._srv_resolver = srv_resolver