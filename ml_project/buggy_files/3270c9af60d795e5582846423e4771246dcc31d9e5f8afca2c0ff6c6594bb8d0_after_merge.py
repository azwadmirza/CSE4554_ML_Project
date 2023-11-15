def destroy(device):
    '''
    Destroy a RAID device.

    WARNING This will zero the superblock of all members of the RAID array..

    CLI Example:

    .. code-block:: bash

        salt '*' raid.destroy /dev/md0
    '''
    try:
        details = detail(device)
    except CommandExecutionError:
        return False

    stop_cmd = ' '.join(['mdadm', '--stop', device])
    zero_cmd = ' '.join(['mdadm', '--zero-superblock'])

    if __salt__['cmd.retcode'](stop_cmd):
        for number in details['members']:
            zero_cmd.append(details['members'][number]['device'])
        __salt__['cmd.retcode'](zero_cmd)

    # Remove entry from config file:
    if __grains__.get('os_family') == 'Debian':
        cfg_file = '/etc/mdadm/mdadm.conf'
    else:
        cfg_file = '/etc/mdadm.conf'

    try:
        __salt__['file.replace'](cfg_file, 'ARRAY {0} .*'.format(device), '')
    except SaltInvocationError:
        pass

    if __salt__['raid.list']().get(device) is None:
        return True
    else:
        return False