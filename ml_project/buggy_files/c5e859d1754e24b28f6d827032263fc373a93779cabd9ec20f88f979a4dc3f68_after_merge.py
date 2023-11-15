    def _normalize_san(self, san):
        # apperently openssl returns 'IP address' not 'IP' as specifier when converting the subjectAltName to string
        # although it won't accept this specifier when generating the CSR. (https://github.com/openssl/openssl/issues/4004)
        if san.startswith('IP Address:'):
            san = 'IP:' + san[len('IP Address:'):]
        if san.startswith('IP:'):
            ip = ipaddress.ip_address(san[3:])
            san = 'IP:{0}'.format(ip.compressed)
        return san