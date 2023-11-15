    def pack(self, data):
        # If the address_type is omitted we assume it's a IPv4 address
        if len(data) == 2 or data[0] == ADDRESS_TYPE_IPV4:
            offset = int(len(data) == 3)
            return struct.pack('>B4sH', ADDRESS_TYPE_IPV4, socket.inet_aton(data[offset]), data[offset + 1])

        host = data[1].encode()
        return struct.pack('>BB', data[0], len(host)) + host + struct.pack('>H', data[2])