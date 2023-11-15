def info(name):
    '''
    Returns information about a container.

    .. code-block:: bash

        salt '*' lxc.info name
    '''
    f = '/var/lib/lxc/{0}/config'.format(name)
    cgroup_dir = '/sys/fs/cgroup/memory/lxc/{0}/'.format(name)
    if not os.path.isfile(f):
        return None

    ret = {}

    config = [(v[0].strip(), v[1].strip()) for v in
              [l.split('#', 1)[0].strip().split('=', 1) for l in
               open(f).readlines()] if len(v) == 2]

    ifaces = []
    current = None

    for k, v in config:
        if k == 'lxc.network.type':
            current = {'type': v}
            ifaces.append(current)
        elif not current:
            continue
        elif k.startswith('lxc.network.'):
            current[k.replace('lxc.network.', '', 1)] = v
    if ifaces:
        ret['ifaces'] = ifaces

    ret['rootfs'] = next((i[1] for i in config if i[0] == 'lxc.rootfs'), None)
    ret['state'] = state(name)

    if ret['state'] == 'running':
        with open(cgroup_dir + 'memory.limit_in_bytes') as f:
            limit = int(f.read())
        with open(cgroup_dir + 'memory.usage_in_bytes') as f:
            memory = int(f.read())
        free = limit - memory
        ret['memory_limit'] = limit
        ret['memory_free'] = free

    return ret