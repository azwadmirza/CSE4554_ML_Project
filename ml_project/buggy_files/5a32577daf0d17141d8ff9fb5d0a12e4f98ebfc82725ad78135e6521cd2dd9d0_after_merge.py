def list_nodes(kwargs=None, call=None):  # pylint: disable=W0613
    '''
    Return a list of the VMs that are on the provider
    '''
    ret = {}
    conn = get_conn()
    nodes = conn.get_registered_vms()
    for node in nodes:
        instance = conn.get_vm_by_path(node)
        properties = salt.utils.cloud.simple_types_filter(
            instance.get_properties()
        )
        ret[properties['name']] = {
            'id': properties['name'],
            'ram': properties['memory_mb'],
            'cpus': properties['num_cpu'],
        }
        if 'ip_address' in properties:
            ret[properties['name']]['ip_address'] = properties['ip_address']
    return ret