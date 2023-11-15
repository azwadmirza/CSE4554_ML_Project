def enc(data, **kwargs):
    '''
    Alias to `{box_type}_encrypt`

    box_type: secretbox, sealedbox(default)
    '''
    box_type = _get_config(**kwargs)['box_type']
    if box_type == 'sealedbox':
        return sealedbox_encrypt(data, **kwargs)
    if box_type == 'secretbox':
        return secretbox_encrypt(data, **kwargs)
    return sealedbox_encrypt(data, **kwargs)