def status(name):
    '''
    Check the status of a gluster volume.

    name
        Volume name

    CLI Example:

    .. code-block:: bash

        salt '*' glusterfs.status myvolume
    '''
    # Get minor version
    minor_version = _get_minor_version()
    # Get volume status
    cmd = 'gluster volume status {0}'.format(name)
    result = __salt__['cmd.run'](cmd).splitlines()
    if 'does not exist' in result[0]:
        return result[0]
    if 'is not started' in result[0]:
        return result[0]

    ret = {'bricks': {}, 'nfs': {}, 'healers': {}}
    # Iterate line by line, concatenating lines the gluster cli separated
    for line_number in range(len(result)):
        line = result[line_number]
        if line.startswith('Brick'):
            # See if this line is broken up into multiple lines
            while len(line.split()) < 5:
                line_number = line_number + 1
                line = line.rstrip() + result[line_number]

            # Parse Brick data
            if minor_version >= 7:
                brick, port, port_rdma, online, pid = line.split()[1:]
            else:
                brick, port, online, pid = line.split()[1:]
            host, path = brick.split(':')
            data = {'port': port, 'pid': pid, 'host': host, 'path': path}
            if online == 'Y':
                data['online'] = True
            else:
                data['online'] = False
            # Store, keyed by <host>:<brick> string
            ret['bricks'][brick] = data
        elif line.startswith('NFS Server on'):
            # See if this line is broken up into multiple lines
            while len(line.split()) < 5:
                line_number = line_number + 1
                line = line.rstrip() + result[line_number]

            # Parse NFS Server data
            if minor_version >= 7:
                host, port, port_rdma, online, pid = line.split()[3:]
            else:
                host, port, online, pid = line.split()[3:]
            data = {'port': port, 'pid': pid}
            if online == 'Y':
                data['online'] = True
            else:
                data['online'] = False
            # Store, keyed by hostname
            ret['nfs'][host] = data
        elif line.startswith('Self-heal Daemon on'):
            # See if this line is broken up into multiple lines
            while len(line.split()) < 5:
                line_number = line_number + 1
                line = line.rstrip() + result[line_number]

            # Parse NFS Server data
            if minor_version >= 7:
                host, port, port_rdma, online, pid = line.split()[3:]
            else:
                host, port, online, pid = line.split()[3:]
            data = {'port': port, 'pid': pid}
            if online == 'Y':
                data['online'] = True
            else:
                data['online'] = False
            # Store, keyed by hostname
            ret['healers'][host] = data
    return ret