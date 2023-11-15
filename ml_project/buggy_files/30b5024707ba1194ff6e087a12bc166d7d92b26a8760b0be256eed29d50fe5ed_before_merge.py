def mk_token(opts, tdata):
    '''
    Mint a new token using the config option hash_type and store tdata with 'token' attribute set
    to the token.
    This module uses the hash of random 512 bytes as a token.

    :param opts: Salt master config options
    :param tdata: Token data to be stored with 'token' attirbute of this dict set to the token.
    :returns: tdata with token if successful. Empty dict if failed.
    '''
    hash_type = getattr(hashlib, opts.get('hash_type', 'md5'))
    tok = six.text_type(hash_type(os.urandom(512)).hexdigest())
    t_path = os.path.join(opts['token_dir'], tok)
    while os.path.isfile(t_path):
        tok = six.text_type(hash_type(os.urandom(512)).hexdigest())
        t_path = os.path.join(opts['token_dir'], tok)
    tdata['token'] = tok
    serial = salt.payload.Serial(opts)
    try:
        with salt.utils.files.set_umask(0o177):
            with salt.utils.files.fopen(t_path, 'w+b') as fp_:
                fp_.write(serial.dumps(tdata))
    except (IOError, OSError):
        log.warning(
            'Authentication failure: can not write token file "%s".', t_path)
        return {}
    return tdata