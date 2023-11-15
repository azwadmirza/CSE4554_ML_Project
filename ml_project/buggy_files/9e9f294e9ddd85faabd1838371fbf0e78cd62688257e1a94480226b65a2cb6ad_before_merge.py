def list_peers():
    '''
    Return a list of gluster peers

    CLI Example:

    .. code-block:: bash

        salt '*' glusterfs.list_peers

    GLUSTER direct CLI example (to show what salt is sending to gluster):

        $ gluster peer status

    GLUSTER CLI 3.4.4 return example (so we know what we are parsing):

        Number of Peers: 2

        Hostname: ftp2
        Port: 24007
        Uuid: cbcb256b-e66e-4ec7-a718-21082d396c24
        State: Peer in Cluster (Connected)

        Hostname: ftp3
        Uuid: 5ea10457-6cb2-427b-a770-7897509625e9
        State: Peer in Cluster (Connected)


    '''
    root = _gluster_xml('peer status')
    result = [x.find('hostname').text for x in _iter(root, 'peer')]
    if len(result) == 0:
        return None
    else:
        return result