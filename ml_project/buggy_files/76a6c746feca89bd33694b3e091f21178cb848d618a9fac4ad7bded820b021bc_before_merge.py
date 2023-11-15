def _get_driver(profile):
    config = __salt__['config.option']('libcloud_dns')[profile]
    cls = get_driver(config['driver'])
    key = config.get('key')
    secret = config.get('secret', None)
    secure = config.get('secure', True)
    host = config.get('jost', None)
    port = config.get('port', None)
    return cls(key, secret, secure, host, port)