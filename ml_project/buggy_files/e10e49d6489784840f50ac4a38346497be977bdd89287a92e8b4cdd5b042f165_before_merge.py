def _parse_network_settings(opts, current):
    '''
    Filters given options and outputs valid settings for
    the global network settings file.
    '''
    # Normalize keys
    opts = dict((k.lower(), v) for (k, v) in six.iteritems(opts))
    current = dict((k.lower(), v) for (k, v) in six.iteritems(current))

    # Check for supported parameters
    retain_settings = opts.get('retain_settings', False)
    result = current if retain_settings else {}

    valid = _CONFIG_TRUE + _CONFIG_FALSE
    if 'enabled' not in opts:
        try:
            opts['networking'] = current['networking']
            _log_default_network('networking', current['networking'])
        except ValueError:
            _raise_error_network('networking', valid)
    else:
        opts['networking'] = opts['enabled']

    if opts['networking'] in valid:
        if opts['networking'] in _CONFIG_TRUE:
            result['networking'] = 'yes'
        elif opts['networking'] in _CONFIG_FALSE:
            result['networking'] = 'no'
    else:
        _raise_error_network('networking', valid)

    if 'hostname' not in opts:
        try:
            opts['hostname'] = current['hostname']
            _log_default_network('hostname', current['hostname'])
        except Exception:
            _raise_error_network('hostname', ['server1.example.com'])

    if opts['hostname']:
        result['hostname'] = opts['hostname']
    else:
        _raise_error_network('hostname', ['server1.example.com'])

    if 'nozeroconf' in opts:
        if opts['nozeroconf'] in valid:
            if opts['nozeroconf'] in _CONFIG_TRUE:
                result['nozeroconf'] = 'true'
            elif opts['nozeroconf'] in _CONFIG_FALSE:
                result['nozeroconf'] = 'false'
        else:
            _raise_error_network('nozeroconf', valid)

    for opt in opts:
        if opt not in ['networking', 'hostname', 'nozeroconf']:
            result[opt] = opts[opt]
    return result