def dec(data, **kwargs):
    '''
    Alias to `{box_type}_decrypt`

    box_type: secretbox, sealedbox(default)
    '''
    box_type = _get_config(**kwargs)['box_type']
    if box_type == 'sealedbox':
        return sealedbox_decrypt(data, **kwargs)
    if box_type == 'secretbox':
        return secretbox_decrypt(data, **kwargs)
    return sealedbox_decrypt(data, **kwargs)