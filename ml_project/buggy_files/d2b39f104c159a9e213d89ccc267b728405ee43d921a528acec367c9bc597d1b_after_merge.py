def load_ssh_public_key(data, backend):
    key_parts = data.split(b' ', 2)

    if len(key_parts) < 2:
        raise ValueError(
            'Key is not in the proper format or contains extra data.')

    key_type = key_parts[0]

    if key_type == b'ssh-rsa':
        loader = _load_ssh_rsa_public_key
    elif key_type == b'ssh-dss':
        loader = _load_ssh_dss_public_key
    elif key_type in [
        b'ecdsa-sha2-nistp256', b'ecdsa-sha2-nistp384', b'ecdsa-sha2-nistp521',
    ]:
        loader = _load_ssh_ecdsa_public_key
    else:
        raise UnsupportedAlgorithm('Key type is not supported.')

    key_body = key_parts[1]

    try:
        decoded_data = base64.b64decode(key_body)
    except TypeError:
        raise ValueError('Key is not in the proper format.')

    inner_key_type, rest = _read_next_string(decoded_data)

    if inner_key_type != key_type:
        raise ValueError(
            'Key header and key body contain different key type values.'
        )

    return loader(key_type, rest, backend)