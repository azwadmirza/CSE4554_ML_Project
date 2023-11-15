def decode_values(values_str):
    values = []
    index = 0
    while index < len(values_str):
        length = unpack_from('!H', values_str[index:])[0]
        index += calcsize('!H')
        values.append(values_str[index:index + length].decode('utf-8'))
        index += length
    return values