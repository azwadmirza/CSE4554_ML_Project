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

    # Default quote type is an empty string, which will not quote values
    quote_type = ''

    valid = _CONFIG_TRUE + _CONFIG_FALSE
    if 'enabled' not in opts:
        try:
            opts['networking'] = current['networking']
            # If networking option is quoted, use its quote type
            quote_type = salt.utils.is_quoted(opts['networking'])
            _log_default_network('networking', current['networking'])
        except ValueError:
            _raise_error_network('networking', valid)
    else:
        opts['networking'] = opts['enabled']

    true_val = '{0}yes{0}'.format(quote_type)
    false_val = '{0}no{0}'.format(quote_type)

    networking = salt.utils.dequote(opts['networking'])
    if networking in valid:
        if networking in _CONFIG_TRUE:
            result['networking'] = true_val
        elif networking in _CONFIG_FALSE:
            result['networking'] = false_val
    else:
        _raise_error_network('networking', valid)

    if 'hostname' not in opts:
        try:
            opts['hostname'] = current['hostname']
            _log_default_network('hostname', current['hostname'])
        except Exception:
            _raise_error_network('hostname', ['server1.example.com'])

    if opts['hostname']:
        result['hostname'] = '{1}{0}{1}'.format(
            salt.utils.dequote(opts['hostname']), quote_type)
    else:
        _raise_error_network('hostname', ['server1.example.com'])

    if 'nozeroconf' in opts:
        nozeroconf = salt.utils.dequote(opts['nozerconf'])
        if nozeroconf in valid:
            if nozeroconf in _CONFIG_TRUE:
                result['nozeroconf'] = true_val
            elif nozeroconf in _CONFIG_FALSE:
                result['nozeroconf'] = false_val
        else:
            _raise_error_network('nozeroconf', valid)

    for opt in opts:
        if opt not in ['networking', 'hostname', 'nozeroconf']:
            result[opt] = '{1}{0}{1}'.format(
                salt.utils.dequote(opts[opt]), quote_type)
    return result