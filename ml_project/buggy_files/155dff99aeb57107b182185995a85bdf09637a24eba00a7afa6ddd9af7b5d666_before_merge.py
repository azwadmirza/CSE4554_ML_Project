def encode_values(values):
    return ''.join([pack('!H', len(value)) + str(value) for value in values])