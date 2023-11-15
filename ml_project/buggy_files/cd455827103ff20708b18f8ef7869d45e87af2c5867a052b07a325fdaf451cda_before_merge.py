def _get_options(ret=None):
    '''
    Returns options used for the MySQL connection.
    '''
    defaults = {'host': 'salt',
                'user': 'salt',
                'pass': 'salt',
                'db': 'salt',
                'port': 3306,
                'ssl_ca': None,
                'ssl_cert': None,
                'ssl_key': None}

    attrs = {'host': 'host',
             'user': 'user',
             'pass': 'pass',
             'db': 'db',
             'port': 'port',
             'ssl_ca': 'ssl_ca',
             'ssl_cert': 'ssl_cert',
             'ssl_key': 'ssl_key'}

    _options = salt.returners.get_returner_options(__virtualname__,
                                                   ret,
                                                   attrs,
                                                   __salt__=__salt__,
                                                   __opts__=__opts__,
                                                   defaults=defaults)
    # Ensure port is an int
    if 'port' in _options:
        _options['port'] = int(_options['port'])
    return _options