def __decode_address(address_type, offset, data):
    if address_type == ADDRESS_TYPE_IPV4:
        destination_address = socket.inet_ntoa(data[offset:offset + 4])
        offset += 4
    elif address_type == ADDRESS_TYPE_DOMAIN_NAME:
        domain_length, = struct.unpack_from("!B", data, offset)
        offset += 1
        destination_address = data[offset:offset + domain_length]
        offset += domain_length
    elif address_type == ADDRESS_TYPE_IPV6:
        raise IPV6AddrError()
    else:
        raise ValueError("Unsupported address type %r" % address_type )

    return offset, destination_address