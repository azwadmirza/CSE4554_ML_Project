def save_config():
    '''
    Save RAID configuration to config file.

    Same as:
    mdadm --detail --scan >> /etc/mdadm/mdadm.conf

    Fixes this issue with Ubuntu
    REF: http://askubuntu.com/questions/209702/why-is-my-raid-dev-md1-showing-up-as-dev-md126-is-mdadm-conf-being-ignored

    CLI Example:

    .. code-block:: bash

        salt '*' raid.save_config

    '''
    scan = __salt__['cmd.run']('mdadm --detail --scan', python_shell=False).splitlines()
    # Issue with mdadm and ubuntu
    # REF: http://askubuntu.com/questions/209702/why-is-my-raid-dev-md1-showing-up-as-dev-md126-is-mdadm-conf-being-ignored
    if __grains__['os'] == 'Ubuntu':
        buggy_ubuntu_tags = ['name', 'metadata']
        for i, elem in enumerate(scan):
            for bad_tag in buggy_ubuntu_tags:
                pattern = r'\s{0}=\S+'.format(re.escape(bad_tag))
                pattern = re.compile(pattern, flags=re.I)
                scan[i] = re.sub(pattern, '', scan[i])

    if __grains__.get('os_family') == 'Debian':
        cfg_file = '/etc/mdadm/mdadm.conf'
    else:
        cfg_file = '/etc/mdadm.conf'

    try:
        vol_d = dict([(line.split()[1], line) for line in scan])
        for vol in vol_d:
            pattern = r'^ARRAY\s+{0}'.format(re.escape(vol))
            __salt__['file.replace'](cfg_file, pattern, vol_d[vol], append_if_not_found=True)
    except SaltInvocationError:  # File is missing
        __salt__['file.write'](cfg_file, args=scan)

    return __salt__['cmd.run']('update-initramfs -u')