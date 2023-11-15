    def unpack(self, data, offset, unpack_list):
        address_type, = struct.unpack_from('>B', data, offset)
        offset += 1

        if address_type == ADDRESS_TYPE_IPV4:
            host = socket.inet_ntoa(data[offset:offset + 4])
            port, = struct.unpack_from('>H', data, offset + 4)
            offset += 6
            address = UDPv4Address(host, port)
        elif address_type == ADDRESS_TYPE_DOMAIN_NAME:
            domain_length, = struct.unpack_from('>B', data, offset)
            offset += 1
            try:
                host = data[offset:offset + domain_length]
                host = host.decode()
            except UnicodeDecodeError as e:
                raise InvalidAddressException(f'Invalid address: {host}') from e
            port, = struct.unpack_from('>H', data, offset + domain_length)
            offset += domain_length + 2
            address = DomainAddress(host, port)
        elif address_type == ADDRESS_TYPE_IPV6:
            raise IPV6AddrError()
        else:
            raise InvalidAddressException('Invalid address type')

        unpack_list.append(address)
        return offset