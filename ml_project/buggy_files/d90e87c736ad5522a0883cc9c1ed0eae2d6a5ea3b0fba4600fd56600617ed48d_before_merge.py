def _init_client():
    '''Setup client and init datastore.
    '''
    global client, path_prefix
    if client is not None:
        return

    etcd_kwargs = {
            'host': __opts__.get('etcd.host', '127.0.0.1'),
            'port': __opts__.get('etcd.port', 2379),
            'protocol': __opts__.get('etcd.protocol', 'http'),
            'allow_reconnect': __opts__.get('etcd.allow_reconnect', True),
            'allow_redirect': __opts__.get('etcd.allow_redirect', False),
            'srv_domain': __opts__.get('etcd.srv_domain', None),
            'read_timeout': __opts__.get('etcd.read_timeout', 60),
            'username': __opts__.get('etcd.username', None),
            'password': __opts__.get('etcd.password', None),
            'cert': __opts__.get('etcd.cert', None),
            'ca_cert': __opts__.get('etcd.ca_cert', None),
    }
    path_prefix = __opts__.get('etcd.path_prefix', _DEFAULT_PATH_PREFIX)
    if path_prefix != "":
        path_prefix = '/{0}'.format(path_prefix.strip('/'))
    log.info("etcd: Setting up client with params: %r", etcd_kwargs)
    client = etcd.Client(**etcd_kwargs)
    try:
        client.get(path_prefix)
    except etcd.EtcdKeyNotFound:
        log.info("etcd: Creating dir %r", path_prefix)
        client.write(path_prefix, None, dir=True)