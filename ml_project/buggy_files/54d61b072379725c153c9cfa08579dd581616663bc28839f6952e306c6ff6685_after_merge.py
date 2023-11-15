def _get_sk(**kwargs):
    '''
    Return sk
    '''
    config = _get_config(**kwargs)
    key = None
    if config['sk']:
        key = salt.utils.stringutils.to_str(config['sk'])
    sk_file = config['sk_file']
    if not key and sk_file:
        try:
            with salt.utils.files.fopen(sk_file, 'rb') as keyf:
                key = salt.utils.stringutils.to_unicode(keyf.read()).rstrip('\n')
        except (IOError, OSError):
            raise Exception('no key or sk_file found')
    return base64.b64decode(key)