def _get_pk(**kwargs):
    '''
    Return pk
    '''
    config = _get_config(**kwargs)
    pubkey = salt.utils.stringutils.to_str(config['pk'])
    pk_file = config['pk_file']
    if not pubkey and pk_file:
        with salt.utils.files.fopen(pk_file, 'rb') as keyf:
            pubkey = salt.utils.stringutils.to_unicode(keyf.read()).rstrip('\n')
    if pubkey is None:
        raise Exception('no pubkey or pk_file found')
    pubkey = six.text_type(pubkey)
    return base64.b64decode(pubkey)