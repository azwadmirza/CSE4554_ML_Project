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
                [start=(true|false)]

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
        If true, start the newly created container.
    '''
    nicp = _nic_profile(nic)
    start_ = kwargs.pop('start', False)
    with tempfile.NamedTemporaryFile() as cfile:
        cfile.write(_gen_config(cpuset=cpuset, cpushare=cpushare,
                                memory=memory, nicp=nicp))
        cfile.flush()
        ret = create(name, config=cfile.name, profile=profile)
    if start_ and ret['created']:
        ret['state'] = start(name)['state']
    else:
        ret['state'] = state(name)
    return ret