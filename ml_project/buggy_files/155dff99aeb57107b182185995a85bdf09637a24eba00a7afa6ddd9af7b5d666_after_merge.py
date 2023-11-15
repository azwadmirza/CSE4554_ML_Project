def encode_values(values):
    encoded_list = [value.encode('utf-8') for value in values]
    return ''.join([pack('!H', len(encoded)) + encoded for encoded in encoded_list])