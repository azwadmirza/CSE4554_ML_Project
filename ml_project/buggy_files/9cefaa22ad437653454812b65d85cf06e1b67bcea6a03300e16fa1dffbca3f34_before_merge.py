def _get_conn(opts, profile=None):
    '''
    Establish a connection to etcd
    '''
    if profile is None:
        profile = opts.get('etcd.returner')
    path = opts.get('etcd.returner_root', '/salt/return')
    return salt.utils.etcd_util.get_conn(opts, profile), path