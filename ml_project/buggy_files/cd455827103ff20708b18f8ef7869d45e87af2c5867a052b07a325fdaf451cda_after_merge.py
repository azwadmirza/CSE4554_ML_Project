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
    # post processing
    for k, v in _options.iteritems():
        if isinstance(v, string_types) and v.lower() == 'none':
            # Ensure 'None' is rendered as None
            _options[k] = None
        if k == 'port':
            # Ensure port is an int
            _options[k] = int(v)

    return _options