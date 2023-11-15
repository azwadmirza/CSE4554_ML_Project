def get_zone():
    '''
    Get current timezone (i.e. America/Denver)

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_zone
    '''
    cmd = ''
    if salt.utils.which('timedatectl'):
        ret = _timedatectl()

        for line in (x.strip() for x in ret['stdout'].splitlines()):
            try:
                return re.match(r'Time ?zone:\s+(\S+)', line).group(1)
            except AttributeError:
                pass

        msg = ('Failed to parse timedatectl output: {0}\n'
               'Please file an issue with SaltStack').format(ret['stdout'])
        raise CommandExecutionError(msg)

    else:
        if __grains__['os'].lower() == 'centos':
            return _get_zone_etc_localtime()
        os_family = __grains__['os_family']
        for family in ('RedHat', 'Suse'):
            if family in os_family:
                return _get_zone_sysconfig()
        for family in ('Debian', 'Gentoo'):
            if family in os_family:
                return _get_zone_etc_timezone()
        if os_family in ('FreeBSD', 'OpenBSD', 'NetBSD'):
            return _get_zone_etc_localtime()
        elif 'Solaris' in os_family:
            return _get_zone_solaris()
    raise CommandExecutionError('Unable to get timezone')