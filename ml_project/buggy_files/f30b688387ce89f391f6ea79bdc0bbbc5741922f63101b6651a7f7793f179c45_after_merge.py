def get_hwclock():
    '''
    Get current hardware clock setting (UTC or localtime)

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.get_hwclock
    '''
    cmd = ''
    if salt.utils.which('timedatectl'):
        ret = _timedatectl()
        for line in (x.strip() for x in ret['stdout'].splitlines()):
            if 'rtc in local tz' in line.lower():
                try:
                    if line.split(':')[-1].strip().lower() == 'yes':
                        return 'localtime'
                    else:
                        return 'UTC'
                except IndexError:
                    pass

        msg = ('Failed to parse timedatectl output: {0}\n'
               'Please file an issue with SaltStack').format(ret['stdout'])
        raise CommandExecutionError(msg)

    else:
        os_family = __grains__['os_family']
        for family in ('RedHat', 'Suse'):
            if family in os_family:
                cmd = ['tail', '-n', '1', '/etc/adjtime']
                return __salt__['cmd.run'](cmd, python_shell=False)
        if 'Debian' in __grains__['os_family']:
            # Original way to look up hwclock on Debian-based systems
            try:
                with salt.utils.fopen('/etc/default/rcS', 'r') as fp_:
                    for line in fp_:
                        if re.match(r'^\s*#', line):
                            continue
                        if 'UTC=' in line:
                            is_utc = line.rstrip('\n').split('=')[-1].lower()
                            if is_utc == 'yes':
                                return 'UTC'
                            else:
                                return 'localtime'
            except IOError as exc:
                pass
            # Since Wheezy
            cmd = ['tail', '-n', '1', '/etc/adjtime']
            return __salt__['cmd.run'](cmd, python_shell=False)
        elif 'Gentoo' in __grains__['os_family']:
            offset_file = '/etc/conf.d/hwclock'
            try:
                with salt.utils.fopen(offset_file, 'r') as fp_:
                    for line in fp_:
                        if line.startswith('clock='):
                            line = line.rstrip('\n')
                            return line.split('=')[-1].strip('\'"')
                    raise CommandExecutionError(
                        'Offset information not found in {0}'.format(
                            offset_file
                        )
                    )
            except IOError as exc:
                raise CommandExecutionError(
                    'Problem reading offset file {0}: {1}'
                    .format(offset_file, exc.strerror)
                )
        elif 'Solaris' in __grains__['os_family']:
            offset_file = '/etc/rtc_config'
            try:
                with salt.utils.fopen(offset_file, 'r') as fp_:
                    for line in fp_:
                        if line.startswith('zone_info=GMT'):
                            return 'UTC'
                    return 'localtime'
            except IOError as exc:
                if exc.errno == errno.ENOENT:
                    # offset file does not exist
                    return 'UTC'
                raise CommandExecutionError(
                    'Problem reading offset file {0}: {1}'
                    .format(offset_file, exc.strerror)
                )