def peer(name):
    '''
    Add another node into the peer list.

    name
        The remote host to probe.

    CLI Example:

    .. code-block:: bash

        salt 'one.gluster.*' glusterfs.peer two

    GLUSTER direct CLI example (to show what salt is sending to gluster):

        $ gluster peer probe ftp2

    GLUSTER CLI 3.4.4 return example (so we know what we are parsing):
        #if the "peer" is the local host:
        peer probe: success: on localhost not needed

        #if the peer was just added:
        peer probe: success

        #if the peer was already part of the cluster:
        peer probe: success: host ftp2 port 24007 already in peer list



    '''
    if suc.check_name(name, 'a-zA-Z0-9._-'):
        raise SaltInvocationError(
            'Invalid characters in peer name "{0}"'.format(name))

    cmd = 'peer probe {0}'.format(name)

    op_result = {
        "exitval": _gluster_xml(cmd).find('opErrno').text,
        "output": _gluster_xml(cmd).find('output').text
    }
    return op_result