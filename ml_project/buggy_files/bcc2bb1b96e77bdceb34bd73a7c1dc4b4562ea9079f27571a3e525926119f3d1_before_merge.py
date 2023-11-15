def valid_id(opts, id_):
    '''
    Returns if the passed id is valid
    '''
    return bool(clean_path(opts['pki_dir'], id_))