def blkid(device=None):
    '''
    Return block device attributes: UUID, LABEL, etc.  This function only works
    on systems where blkid is available.

    CLI Example:

    .. code-block:: bash

        salt '*' disk.blkid
        salt '*' disk.blkid /dev/sda
    '''
    args = ""
    if device:
        args = " " + device

    ret = {}
    blkid_result = __salt__['cmd.run_all']('blkid' + args, python_shell=False)
    if blkid_result['retcode'] > 0:
        return ret
    for line in blkid_result['stdout'].split('\n'):
        comps = line.split()
        device = comps[0][:-1]
        info = {}
        device_attributes = re.split(('\"*\"'), line.partition(' ')[2])
        for key, value in zip(*[iter(device_attributes)]*2):
            key = key.strip('=').strip(' ')
            info[key] = value.strip('"')
        ret[device] = info

    return ret