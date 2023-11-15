def dec(data, **kwargs):
    '''
    Alias to `{box_type}_decrypt`

    box_type: secretbox, sealedbox(default)
    '''
    if 'keyfile' in kwargs:
        salt.utils.versions.warn_until(
            'Fluorine',
            'The \'keyfile\' argument has been deprecated and will be removed in Salt '
            '{version}. Please use \'sk_file\' argument instead.'
        )
        kwargs['sk_file'] = kwargs['keyfile']

        # set boxtype to `secretbox` to maintain backward compatibility
        kwargs['box_type'] = 'secretbox'

    if 'key' in kwargs:
        salt.utils.versions.warn_until(
            'Fluorine',
            'The \'key\' argument has been deprecated and will be removed in Salt '
            '{version}. Please use \'sk\' argument instead.'
        )
        kwargs['sk'] = kwargs['key']

        # set boxtype to `secretbox` to maintain backward compatibility
        kwargs['box_type'] = 'secretbox'

    # ensure data is in bytes
    data = salt.utils.stringutils.to_bytes(data)

    box_type = _get_config(**kwargs)['box_type']
    if box_type == 'sealedbox':
        return sealedbox_decrypt(data, **kwargs)
    if box_type == 'secretbox':
        return secretbox_decrypt(data, **kwargs)
    return sealedbox_decrypt(data, **kwargs)