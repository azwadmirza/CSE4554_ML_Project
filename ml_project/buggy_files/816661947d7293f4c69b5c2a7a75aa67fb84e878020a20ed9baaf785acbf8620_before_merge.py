def zone_compare(timezone):
    '''
    Checks the md5sum between the given timezone, and the one set in
    /etc/localtime. Returns True if they match, and False if not. Mostly useful
    for running state checks.

    CLI Example:

    .. code-block:: bash

        salt '*' timezone.zone_compare 'America/Denver'
    '''
    if 'Solaris' in __grains__['os_family']:
        return 'Not implemented for Solaris family'

    tzfile = '/etc/localtime'
    zonepath = '/usr/share/zoneinfo/{0}'.format(timezone)

    if not os.path.exists(tzfile):
        return 'Error: {0} does not exist.'.format(tzfile)

    with salt.utils.fopen(zonepath, 'r') as fp_:
        usrzone = hashlib.md5(fp_.read()).hexdigest()

    with salt.utils.fopen(tzfile, 'r') as fp_:
        etczone = hashlib.md5(fp_.read()).hexdigest()

    if usrzone == etczone:
        return True
    return False