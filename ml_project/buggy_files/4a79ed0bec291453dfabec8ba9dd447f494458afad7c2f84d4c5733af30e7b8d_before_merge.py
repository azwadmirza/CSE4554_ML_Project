    def __init__(self, hostname, verify_certs):
        self._verify_certs = verify_certs

        if isIPAddress(hostname) or isIPv6Address(hostname):
            self._hostnameBytes = hostname.encode("ascii")
            self._is_ip_address = True
        else:
            # twisted's ClientTLSOptions falls back to the stdlib impl here if
            # idna is not installed, but points out that lacks support for
            # IDNA2008 (http://bugs.python.org/issue17305).
            #
            # We can rely on having idna.
            self._hostnameBytes = idna.encode(hostname)
            self._is_ip_address = False

        self._hostnameASCII = self._hostnameBytes.decode("ascii")