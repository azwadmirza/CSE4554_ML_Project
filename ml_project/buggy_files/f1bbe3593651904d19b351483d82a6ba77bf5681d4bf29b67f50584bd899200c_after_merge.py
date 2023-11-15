        def make_connection(self, host):
            scheme = urlparse(host).scheme
            if not scheme:
                scheme = NEOS.scheme

            # Empirically, the connection class in Python 3.x needs to
            # match the final endpoint connection scheme, NOT the proxy
            # scheme.  The set_tunnel host then should NOT have a scheme
            # attached to it.
            if scheme == 'https':
                connClass = httplib.HTTPSConnection
            else:
                connClass = httplib.HTTPConnection

            connection = connClass(self.proxy.hostname, self.proxy.port)
            connection.set_tunnel(host)
            return connection