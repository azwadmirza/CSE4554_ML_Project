def init(name,
         cpuset=None,
         cpushare=None,
         memory=None,
         nic='default',
         profile=None,
         **kwargs):
    '''
    Initialize a new container.

    .. code-block:: bash

        salt 'minion' lxc.init name [cpuset=cgroups_cpuset] \\
                [cpushare=cgroups_cpushare] [memory=cgroups_memory] \\
                [nic=nic_profile] [profile=lxc_profile] \\
                [start=(true|false)] [seed=(true|false)] \\
                [install=(true|false)] [config=minion_config]

    name
        Name of the container.

    cpuset
        cgroups cpuset.

    cpushare
        cgroups cpu shares.

    memory
        cgroups memory limit, in MB.

    nic
        Network interfaces profile (defined in config or pillar).

    profile
        A LXC profile (defined in config or pillar).

    start
        Start the newly created container.

    seed
        Seed the container with the minion config. Default: true

    install
        If salt-minion is not already installed, install it. Default: true

    config
        Optional config paramers. By default, the id is set to the name of the
        container.
    '''
    nicp = _nic_profile(nic)
    start_ = kwargs.pop('start', False)
    seed = kwargs.pop('seed', True)
    install = kwargs.pop('install', True)
    seed_cmd = kwargs.pop('seed_cmd', None)
    config = kwargs.pop('config', None)

    with tempfile.NamedTemporaryFile() as cfile:
        cfile.write(_gen_config(cpuset=cpuset, cpushare=cpushare,
                                memory=memory, nicp=nicp))
        cfile.flush()
        ret = create(name, config=cfile.name, profile=profile, **kwargs)
    if not ret['created']:
        return ret
    rootfs = info(name)['rootfs']
    if seed:
        __salt__['seed.apply'](rootfs, id_=name, config=config,
                               install=install)
    elif seed_cmd:
        __salt__[seed_cmd](rootfs, name, config)
    if start_ and ret['created']:
        ret['state'] = start(name)['state']
    else:
        ret['state'] = state(name)
    return ret