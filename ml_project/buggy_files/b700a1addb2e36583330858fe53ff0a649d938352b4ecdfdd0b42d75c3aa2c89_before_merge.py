def list_nodes_full():
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
        ret[properties['name']] = {}
        for prop in ('guest_full_name', 'guest_id', 'memory_mb', 'name',
                     'num_cpu', 'path', 'devices', 'disks', 'files',
                     'ip_address', 'net', 'hostname'):
            if prop in properties:
                ret[properties['name']][prop] = properties[prop]
        count = 0
        for disk in ret[properties['name']]['disks']:  # pylint: disable=W0612
            del ret[properties['name']]['disks'][count]['device']['_obj']
            count += 1
        for device in ret[properties['name']]['devices']:
            del ret[properties['name']]['devices'][device]['_obj']
        ret[properties['name']]['status'] = instance.get_status()
        ret[properties['name']]['tools_status'] = instance.get_tools_status()
    return ret