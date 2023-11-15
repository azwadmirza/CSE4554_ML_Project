    def __init__(self, hostname: bytes, verify_certs):
        self._verify_certs = verify_certs

        _decoded = hostname.decode("ascii")
        if isIPAddress(_decoded) or isIPv6Address(_decoded):
            self._is_ip_address = True
        else:
            self._is_ip_address = False

        self._hostnameBytes = hostname
        self._hostnameASCII = self._hostnameBytes.decode("ascii")