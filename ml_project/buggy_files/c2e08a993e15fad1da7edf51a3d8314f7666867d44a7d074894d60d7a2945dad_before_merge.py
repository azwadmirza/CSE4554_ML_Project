def _get_config(**kwargs):
    '''
    Return configuration
    '''
    config = {
        'box_type': 'sealedbox',
        'sk': None,
        'sk_file': '/etc/salt/pki/master/nacl',
        'pk': None,
        'pk_file': '/etc/salt/pki/master/nacl.pub',
    }
    config_key = '{0}.config'.format(__virtualname__)
    try:
        config.update(__salt__['config.get'](config_key, {}))
    except (NameError, KeyError) as e:
        # likly using salt-run so fallback to __opts__
        config.update(__opts__.get(config_key, {}))
    # pylint: disable=C0201
    for k in set(config.keys()) & set(kwargs.keys()):
        config[k] = kwargs[k]
    return config