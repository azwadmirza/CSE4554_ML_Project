def create(name, config=None, profile=None, options=None, **kwargs):
    '''
    Create a new container.

    .. code-block:: bash

        salt 'minion' lxc.create name [config=config_file] \\
                [profile=profile] [template=template_name] \\
                [backing=backing_store] [ vgname=volume_group] \\
                [size=filesystem_size] [options=template_options]

    name
        Name of the container.

    config
        The config file to use for the container. Defaults to system-wide
        config (usually in /etc/lxc/lxc.conf).

    profile
        A LXC profile (defined in config or pillar).

    template
        The template to use. E.g., 'ubuntu' or 'fedora'.

    backing
        The type of storage to use. Set to 'lvm' to use an LVM group. Defaults
        to filesystem within /var/lib/lxc/.

    vgname
        Name of the LVM volume group in which to create the volume for this
        container. Only applicable if backing=lvm. Defaults to 'lxc'.

    size
        Size of the volume to create. Only applicable if backing=lvm.
        Defaults to 1G.

    options
        Template specific options to pass to the lxc-create command.
    '''

    if exists(name):
        return {'created': False, 'error': 'container already exists'}

    cmd = 'lxc-create -n {0}'.format(name)

    profile = _lxc_profile(profile)
    template = kwargs.pop('template', profile.get('template'))
    backing = kwargs.pop('backing', profile.get('backing'))
    vgname = kwargs.pop('vgname', profile.get('vgname'))
    size = kwargs.pop('size', profile.get('size', '1G'))

    if config:
        cmd += ' -f {0}'.format(config)
    if template or profile.get('template'):
        cmd += ' -t {0}'.format(template)
    if backing:
        cmd += ' -B {0}'.format(backing)
        if vgname:
            cmd += ' --vgname {0}'.format(vgname)
        if size:
            cmd += ' --fssize {0}'.format(size)
    if options:
        cmd += ' -- {0}'.format(options)

    ret = __salt__['cmd.run_all'](cmd)
    if ret['retcode'] == 0 and exists(name):
        return {'created': True}
    else:
        if exists(name):
            # destroy the container if it was partially created
            cmd = 'lxc-destroy -n {0}'.format(name)
            __salt__['cmd.retcode'](cmd)
        log.warn('lxc-create failed to create container')
        return {'created': False, 'error': 'container could not be created'}