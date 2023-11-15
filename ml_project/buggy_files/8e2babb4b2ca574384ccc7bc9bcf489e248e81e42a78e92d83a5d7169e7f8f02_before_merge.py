def mod_hostname(hostname):
    '''
    Modify hostname

    .. versionchanged:: 2015.8.0
        Added support for SunOS (Solaris 10, Illumos, SmartOS)

    CLI Example:

    .. code-block:: bash

        salt '*' network.mod_hostname master.saltstack.com
    '''
    #
    # SunOS tested on SmartOS and OmniOS (Solaris 10 compatible)
    # Oracle Solaris 11 uses smf, currently not supported
    #
    # /etc/nodename is the hostname only, not fqdn
    # /etc/defaultdomain is the domain
    # /etc/hosts should have both fqdn and hostname entries
    #

    if hostname is None:
        return False

    hostname_cmd = salt.utils.path.which('hostnamectl') or salt.utils.path.which('hostname')
    if salt.utils.platform.is_sunos():
        uname_cmd = '/usr/bin/uname' if salt.utils.platform.is_smartos() else salt.utils.path.which('uname')
        check_hostname_cmd = salt.utils.path.which('check-hostname')

    # Grab the old hostname so we know which hostname to change and then
    # change the hostname using the hostname command
    if hostname_cmd.endswith('hostnamectl'):
        out = __salt__['cmd.run']('{0} status'.format(hostname_cmd))
        for line in out.splitlines():
            line = line.split(':')
            if 'Static hostname' in line[0]:
                o_hostname = line[1].strip()
    elif not salt.utils.platform.is_sunos():
        # don't run hostname -f because -f is not supported on all platforms
        o_hostname = socket.getfqdn()
    else:
        # output: Hostname core OK: fully qualified as core.acheron.be
        o_hostname = __salt__['cmd.run'](check_hostname_cmd).split(' ')[-1]

    if hostname_cmd.endswith('hostnamectl'):
        __salt__['cmd.run']('{0} set-hostname {1}'.format(hostname_cmd, hostname))
    elif not salt.utils.platform.is_sunos():
        __salt__['cmd.run']('{0} {1}'.format(hostname_cmd, hostname))
    else:
        __salt__['cmd.run']('{0} -S {1}'.format(uname_cmd, hostname.split('.')[0]))

    # Modify the /etc/hosts file to replace the old hostname with the
    # new hostname
    with salt.utils.files.fopen('/etc/hosts', 'r') as fp_:
        host_c = [salt.utils.stringutils.to_unicode(_l)
                  for _l in fp_.readlines()]

    with salt.utils.files.fopen('/etc/hosts', 'w') as fh_:
        for host in host_c:
            host = host.split()

            try:
                host[host.index(o_hostname)] = hostname
                if salt.utils.platform.is_sunos():
                    # also set a copy of the hostname
                    host[host.index(o_hostname.split('.')[0])] = hostname.split('.')[0]
            except ValueError:
                pass

            fh_.write(salt.utils.stringutils.to_str('\t'.join(host) + '\n'))

    # Modify the /etc/sysconfig/network configuration file to set the
    # new hostname
    if __grains__['os_family'] == 'RedHat':
        with salt.utils.files.fopen('/etc/sysconfig/network', 'r') as fp_:
            network_c = [salt.utils.stringutils.to_unicode(_l)
                         for _l in fp_.readlines()]

        with salt.utils.files.fopen('/etc/sysconfig/network', 'w') as fh_:
            for net in network_c:
                if net.startswith('HOSTNAME'):
                    old_hostname = net.split('=', 1)[1].rstrip()
                    quote_type = salt.utils.stringutils.is_quoted(old_hostname)
                    fh_.write(salt.utils.stringutils.to_str(
                        'HOSTNAME={1}{0}{1}\n'.format(
                            salt.utils.stringutils.dequote(hostname),
                            quote_type)))
                else:
                    fh_.write(salt.utils.stringutils.to_str(net))
    elif __grains__['os_family'] in ('Debian', 'NILinuxRT'):
        with salt.utils.files.fopen('/etc/hostname', 'w') as fh_:
            fh_.write(salt.utils.stringutils.to_str(hostname + '\n'))
    elif __grains__['os_family'] == 'OpenBSD':
        with salt.utils.files.fopen('/etc/myname', 'w') as fh_:
            fh_.write(salt.utils.stringutils.to_str(hostname + '\n'))

    # Update /etc/nodename and /etc/defaultdomain on SunOS
    if salt.utils.platform.is_sunos():
        with salt.utils.files.fopen('/etc/nodename', 'w') as fh_:
            fh_.write(salt.utils.stringutils.to_str(
                hostname.split('.')[0] + '\n')
            )
        with salt.utils.files.fopen('/etc/defaultdomain', 'w') as fh_:
            fh_.write(salt.utils.stringutils.to_str(
                ".".join(hostname.split('.')[1:]) + '\n')
            )

    return True