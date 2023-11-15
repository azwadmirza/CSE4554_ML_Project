def returner(ret):
    '''
    Return data to the local syslog
    '''

    _options = _get_options(ret)

    if not _verify_options(_options):
        return

    # Get values from syslog module
    level = getattr(syslog, _options['level'])
    facility = getattr(syslog, _options['facility'])

    # parse for syslog options
    logoption = 0
    for opt in _options['options']:
        logoption = logoption | getattr(syslog, opt)

    # Open syslog correctly based on options and tag
    try:
        if 'tag' in _options:
            syslog.openlog(ident=_options['tag'], logoption=logoption)
        else:
            syslog.openlog(logoption=logoption)
    except TypeError:
        # Python 2.6 syslog.openlog does not accept keyword args
        syslog.openlog(_options.get('tag', 'salt-minion'), logoption)

    # Send log of given level and facility
    syslog.syslog(facility | level, salt.utils.json.dumps(ret))

    # Close up to reset syslog to defaults
    syslog.closelog()