def enc(data, **kwargs):
    '''
    Alias to `{box_type}_encrypt`

    box_type: secretbox, sealedbox(default)
    '''
    if 'keyfile' in kwargs:
        salt.utils.versions.warn_until(
            'Fluorine',
            'The \'keyfile\' argument has been deprecated and will be removed in Salt '
            '{version}. Please use \'sk_file\' argument instead.'
        )
        kwargs['sk_file'] = kwargs['keyfile']

    if 'key' in kwargs:
        salt.utils.versions.warn_until(
            'Fluorine',
            'The \'key\' argument has been deprecated and will be removed in Salt '
            '{version}. Please use \'sk\' argument instead.'
        )
        kwargs['sk'] = kwargs['key']

    # ensure data is in bytes
    data = salt.utils.stringutils.to_bytes(data)

    box_type = _get_config(**kwargs)['box_type']
    if box_type == 'sealedbox':
        return sealedbox_encrypt(data, **kwargs)
    if box_type == 'secretbox':
        return secretbox_encrypt(data, **kwargs)
    return sealedbox_encrypt(data, **kwargs)