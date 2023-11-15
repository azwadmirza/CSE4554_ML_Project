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

    hostname_cmd = salt.utils.which('hostnamectl') or salt.utils.which('hostname')
    if salt.utils.is_sunos():
        uname_cmd = '/usr/bin/uname' if salt.utils.is_smartos() else salt.utils.which('uname')
        check_hostname_cmd = salt.utils.which('check-hostname')

    # Grab the old hostname so we know which hostname to change and then
    # change the hostname using the hostname command
    if hostname_cmd.endswith('hostnamectl'):
        out = __salt__['cmd.run']('{0} status'.format(hostname_cmd))
        for line in out.splitlines():
            line = line.split(':')
            if 'Static hostname' in line[0]:
                o_hostname = line[1].strip()
    elif not salt.utils.is_sunos():
        # don't run hostname -f because -f is not supported on all platforms
        o_hostname = socket.getfqdn()
    else:
        # output: Hostname core OK: fully qualified as core.acheron.be
        o_hostname = __salt__['cmd.run'](check_hostname_cmd).split(' ')[-1]

    if hostname_cmd.endswith('hostnamectl'):
        __salt__['cmd.run']('{0} set-hostname {1}'.format(hostname_cmd, hostname))
    elif not salt.utils.is_sunos():
        __salt__['cmd.run']('{0} {1}'.format(hostname_cmd, hostname))
    else:
        __salt__['cmd.run']('{0} -S {1}'.format(uname_cmd, hostname.split('.')[0]))

    # Modify the /etc/hosts file to replace the old hostname with the
    # new hostname
    with salt.utils.fopen('/etc/hosts', 'r') as fp_:
        host_c = fp_.readlines()

    with salt.utils.fopen('/etc/hosts', 'w') as fh_:
        for host in host_c:
            host = host.split()

            try:
                host[host.index(o_hostname)] = hostname
                if salt.utils.is_sunos():
                    # also set a copy of the hostname
                    host[host.index(o_hostname.split('.')[0])] = hostname.split('.')[0]
            except ValueError:
                pass

            fh_.write('\t'.join(host) + '\n')

    # Modify the /etc/sysconfig/network configuration file to set the
    # new hostname
    if __grains__['os_family'] == 'RedHat':
        with salt.utils.fopen('/etc/sysconfig/network', 'r') as fp_:
            network_c = fp_.readlines()

        with salt.utils.fopen('/etc/sysconfig/network', 'w') as fh_:
            for net in network_c:
                if net.startswith('HOSTNAME'):
                    fh_.write('HOSTNAME={0}\n'.format(hostname))
                else:
                    fh_.write(net)
    elif __grains__['os_family'] in ('Debian', 'NILinuxRT'):
        with salt.utils.fopen('/etc/hostname', 'w') as fh_:
            fh_.write(hostname + '\n')
    elif __grains__['os_family'] == 'OpenBSD':
        with salt.utils.fopen('/etc/myname', 'w') as fh_:
            fh_.write(hostname + '\n')

    # Update /etc/nodename and /etc/defaultdomain on SunOS
    if salt.utils.is_sunos():
        with salt.utils.fopen('/etc/nodename', 'w') as fh_:
            fh_.write(hostname.split('.')[0] + '\n')
        with salt.utils.fopen('/etc/defaultdomain', 'w') as fh_:
            fh_.write(".".join(hostname.split('.')[1:]) + '\n')

    return True