def clone(name,
          orig,
          profile=None,
          network_profile=None,
          nic_opts=None,
          **kwargs):
    '''
    Create a new container as a clone of another container

    name
        Name of the container

    orig
        Name of the original container to be cloned

    profile
        Profile to use in container cloning (see
        :mod:`lxc.get_container_profile
        <salt.modules.lxc.get_container_profile>`). Values in a profile will be
        overridden by the **Container Cloning Arguments** listed below.

    path
        path to the container parent directory
        default: /var/lib/lxc (system)

        .. versionadded:: 2015.8.0

    **Container Cloning Arguments**

    snapshot
        Use Copy On Write snapshots (LVM)

    size : 1G
        Size of the volume to create. Only applicable if ``backing=lvm``.

    backing
        The type of storage to use. Set to ``lvm`` to use an LVM group.
        Defaults to filesystem within /var/lib/lxc.

    network_profile
        Network profile to use for container

        .. versionadded:: 2015.8.0

    nic_opts
        give extra opts overriding network profile values

        .. versionadded:: 2015.8.0


    CLI Examples:

    .. code-block:: bash

        salt '*' lxc.clone myclone orig=orig_container
        salt '*' lxc.clone myclone orig=orig_container snapshot=True
    '''
    profile = get_container_profile(copy.deepcopy(profile))
    kw_overrides = copy.deepcopy(kwargs)

    def select(key, default=None):
        kw_overrides_match = kw_overrides.pop(key, None)
        profile_match = profile.pop(key, default)
        # let kwarg overrides be the preferred choice
        if kw_overrides_match is None:
            return profile_match
        return kw_overrides_match

    path = select('path')
    if exists(name, path=path):
        raise CommandExecutionError(
            'Container \'{0}\' already exists'.format(name)
        )

    _ensure_exists(orig, path=path)
    if state(orig, path=path) != 'stopped':
        raise CommandExecutionError(
            'Container \'{0}\' must be stopped to be cloned'.format(orig)
        )

    backing = select('backing')
    snapshot = select('snapshot')
    if backing in ('dir',):
        snapshot = False
    if not snapshot:
        snapshot = ''
    else:
        snapshot = '-s'

    size = select('size', '1G')
    if backing in ('dir', 'overlayfs', 'btrfs'):
        size = None
    # LXC commands and options changed in 2.0 - CF issue #34086 for details
    if _LooseVersion(version()) >= _LooseVersion('2.0'):
        # https://linuxcontainers.org/lxc/manpages//man1/lxc-copy.1.html
        cmd = 'lxc-copy'
        cmd += ' {0} -n {1} -N {2}'.format(snapshot, orig, name)
    else:
        # https://linuxcontainers.org/lxc/manpages//man1/lxc-clone.1.html
        cmd = 'lxc-clone'
        cmd += ' {0} -o {1} -n {2}'.format(snapshot, orig, name)
    if path:
        cmd += ' -P {0}'.format(pipes.quote(path))
        if not os.path.exists(path):
            os.makedirs(path)
    if backing:
        backing = backing.lower()
        cmd += ' -B {0}'.format(backing)
        if backing not in ('dir', 'overlayfs'):
            if size:
                cmd += ' -L {0}'.format(size)
    ret = __salt__['cmd.run_all'](cmd, python_shell=False)
    # please do not merge extra conflicting stuff
    # inside those two line (ret =, return)
    return _after_ignition_network_profile(cmd,
                                           ret,
                                           name,
                                           network_profile,
                                           path,
                                           nic_opts)