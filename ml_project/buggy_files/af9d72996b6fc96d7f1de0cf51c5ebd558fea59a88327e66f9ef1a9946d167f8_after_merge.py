def list_nodes_min(kwargs=None, call=None):  # pylint: disable=W0613
    '''
    Return a list of the nodes in the provider, with no details
    '''
    log.debug('function list_nodes_min()')
    ret = {}
    conn = get_conn()
    nodes = conn.get_registered_vms()
    for node in nodes:
        comps1 = node.split()
        comps2 = comps1[1].split('/')
        ret[comps2[0]] = True

    return ret