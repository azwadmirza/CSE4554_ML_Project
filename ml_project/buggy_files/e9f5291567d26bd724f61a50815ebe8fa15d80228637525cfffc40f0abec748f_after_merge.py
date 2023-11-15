def unjoin_domain(username=None,
                  password=None,
                  domain=None,
                  workgroup='WORKGROUP',
                  disable=False,
                  restart=False):
    r'''
    Unjoin a computer from an Active Directory Domain. Requires restart.

    :param username:
        Username of an account which is authorized to manage computer accounts
        on the domain. Need to be fully qualified like ``user@domain.tld`` or
        ``domain.tld\user``. If domain not specified, the passed domain will be
        used. If computer account doesn't need to be disabled, can be None.

    :param str password:
        Password of the specified user

    :param str domain: The domain from which to unjoin the computer. Can be None

    :param str workgroup: The workgroup to join the computer to. Default is
    ``WORKGROUP``

        .. versionadded:: 2015.8.2/2015.5.7

    :param bool disable:
        Disable the computer account in Active Directory. True to disable.
        Default is False

    :param bool restart: Restart the computer after successful unjoin

        .. versionadded:: 2015.8.2/2015.5.7

    :returns: Returns a dictionary if successful. False if unsuccessful.
    :rtype: dict, bool

    CLI Example:

    .. code-block:: bash

        salt 'minion-id' system.unjoin_domain restart=True

        salt 'minion-id' system.unjoin_domain username='unjoinuser' \\
                         password='unjoinpassword' disable=True \\
                         restart=True
    '''
    status = get_domain_workgroup()
    if 'Workgroup' in status:
        if status['Workgroup'] == workgroup:
            return 'Already joined to {0}'.format(workgroup)

    if username and '\\' not in username and '@' not in username:
        if domain:
            username = '{0}@{1}'.format(username, domain)
        else:
            return 'Must specify domain if not supplied in username'

    if username and password is None:
        return 'Must specify a password if you pass a username'

    NETSETUP_ACCT_DELETE = 0x4  # pylint: disable=invalid-name

    unjoin_options = 0x0
    if disable:
        unjoin_options |= NETSETUP_ACCT_DELETE

    pythoncom.CoInitialize()
    conn = wmi.WMI()
    comp = conn.Win32_ComputerSystem()[0]
    err = comp.UnjoinDomainOrWorkgroup(Password=password,
                                       UserName=username,
                                       FUnjoinOptions=unjoin_options)

    # you have to do this because UnjoinDomainOrWorkgroup returns a
    # strangely formatted value that looks like (0,)
    if not err[0]:
        err = comp.JoinDomainOrWorkgroup(Name=workgroup)
        if not err[0]:
            ret = {'Workgroup': workgroup,
                   'Restart': False}
            if restart:
                ret['Restart'] = reboot()

            return ret
        else:
            log.error(_lookup_error(err[0]))
            log.error('Failed to join the computer to {0}'.format(workgroup))
            return False
    else:
        log.error(_lookup_error(err[0]))
        log.error('Failed to unjoin computer from {0}'.format(status['Domain']))
        return False