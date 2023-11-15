    def pack(self, data):
        if isinstance(data, DomainAddress):
            host = data[0].encode()
            return struct.pack('>BB', ADDRESS_TYPE_DOMAIN_NAME, len(host)) + host + struct.pack('>H', data[1])
        if isinstance(data, tuple):
            return struct.pack('>B4sH', ADDRESS_TYPE_IPV4, socket.inet_aton(data[0]), data[1])
        raise InvalidAddressException('Invalid address type')