    def _normalize_san(self, san):
        if san.startswith('IP Address:'):
            san = 'IP:' + san[len('IP Address:'):]
        if san.startswith('IP:'):
            ip = ipaddress.ip_address(san[3:])
            san = 'IP:{0}'.format(ip.compressed)
        return san