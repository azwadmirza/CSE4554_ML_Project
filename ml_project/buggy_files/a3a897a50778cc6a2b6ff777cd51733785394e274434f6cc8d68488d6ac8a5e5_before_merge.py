    def unpack(self, data, offset, unpack_list):
        address_type, = struct.unpack_from('>B', data, offset)
        offset += 1

        if address_type == ADDRESS_TYPE_IPV4:
            host = socket.inet_ntoa(data[offset:offset + 4])
            offset += 4
        elif address_type == ADDRESS_TYPE_DOMAIN_NAME:
            domain_length, = struct.unpack_from('>B', data, offset)
            offset += 1
            try:
                host = data[offset:offset + domain_length]
                host = host.decode()
                offset += domain_length
            except UnicodeDecodeError as e:
                raise InvalidAddressException(f'Invalid address: {host}') from e
        elif address_type == ADDRESS_TYPE_IPV6:
            raise IPV6AddrError()
        else:
            raise InvalidAddressException('Invalid address type')

        port, = struct.unpack_from('>H', data, offset)
        offset += 2

        unpack_list.append((host, port))
        return offset