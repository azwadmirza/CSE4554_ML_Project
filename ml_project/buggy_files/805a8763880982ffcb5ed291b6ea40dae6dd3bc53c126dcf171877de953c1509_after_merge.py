def _conf(family='ipv4'):
    '''
    Some distros have a specific location for config files
    '''
    if __grains__['os_family'] == 'RedHat':
        if family == 'ipv6':
            return '/etc/sysconfig/ip6tables'
        else:
            return '/etc/sysconfig/iptables'
    elif __grains__['os_family'] == 'Arch':
        if family == 'ipv6':
            return '/etc/iptables/ip6tables.rules'
        else:
            return '/etc/iptables/iptables.rules'
    elif __grains__['os_family'] == 'Debian':
        if family == 'ipv6':
            return '/etc/iptables/rules.v6'
        else:
            return '/etc/iptables/rules.v4'
    elif __grains__['os'] == 'Gentoo':
        if family == 'ipv6':
            return '/var/lib/ip6tables/rules-save'
        else:
            return '/var/lib/iptables/rules-save'
    elif __grains__['os_family'] == 'Suse':
        # SuSE does not seem to use separate files for IPv4 and IPv6
        return '/etc/sysconfig/scripts/SuSEfirewall2-custom'
    else:
        raise SaltException('Saving iptables to file is not' +
                            ' supported on {0}.'.format(__grains__['os']) +
                            ' Please file an issue with SaltStack')