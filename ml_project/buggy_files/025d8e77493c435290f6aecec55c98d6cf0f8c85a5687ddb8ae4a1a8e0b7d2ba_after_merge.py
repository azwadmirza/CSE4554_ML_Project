def valid_id(opts, id_):
    '''
    Returns if the passed id is valid
    '''
    try:
        return bool(clean_path(opts['pki_dir'], id_))
    except (AttributeError, KeyError, TypeError) as e:
        return False