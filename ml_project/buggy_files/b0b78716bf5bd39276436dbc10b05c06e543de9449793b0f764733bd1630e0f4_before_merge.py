def validate(config):
    '''
    Validate the beacon configuration
    '''
    # Configuration for adb beacon should be a dictionary with states array
    if not isinstance(config, list):
        log.info('Configuration for salt_proxy beacon must be a list.')
        return False, ('Configuration for salt_proxy beacon must be a list.')

    else:
        _config = {}
        list(map(_config.update, config))

        if 'proxies' not in _config:
            return False, ('Configuration for salt_proxy'
                           ' beacon requires proxies.')
        else:
            if not isinstance(_config['proxies'], dict):
                return False, ('Proxies for salt_proxy '
                               'beacon must be a dictionary.')