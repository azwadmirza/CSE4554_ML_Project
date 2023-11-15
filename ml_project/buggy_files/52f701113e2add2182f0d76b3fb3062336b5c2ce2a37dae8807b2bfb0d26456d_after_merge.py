def apply_(path, id_=None, config=None, approve_key=True, install=True):
    '''
    Seed a location (disk image, directory, or block device) with the
    minion config, approve the minion's key, and/or install salt-minion.

    CLI Example:

    .. code-block:: bash

        salt 'minion' seed.whatever path id [config=config_data] \\
                [gen_key=(true|false)] [approve_key=(true|false)] \\
                [install=(true|false)]

    path
        Full path to the directory, device, or disk image  on the target
        minion's file system.

    id
        Minion id with which to seed the path.

    config
        Minion configuration options. By default, the 'master' option is set to
        the target host's 'master'.

    approve_key
        Request a pre-approval of the generated minion key. Requires
        that the salt-master be configured to either auto-accept all keys or
        expect a signing request from the target host. Default: true.

    install
        Install salt-minion, if absent. Default: true.
    '''

    stats = __salt__['file.stats'](path, follow_symlink=True)
    if not stats:
        return '{0} does not exist'.format(path)
    ftype = stats['type']
    path = stats['target']
    mpt = _mount(path, ftype)
    if not mpt:
        return '{0} could not be mounted'.format(path)

    if config is None:
        config = {}
    if not 'master' in config:
        config['master'] = __opts__['master']
    if id_:
        config['id'] = id_

    tmp = os.path.join(mpt, 'tmp')

    # Write the new minion's config to a tmp file
    tmp_config = os.path.join(tmp, 'minion')
    with salt.utils.fopen(tmp_config, 'w+') as fp_:
        fp_.write(yaml.dump(config, default_flow_style=False))

    # Generate keys for the minion
    salt.crypt.gen_keys(tmp, 'minion', 2048)
    pubkeyfn = os.path.join(tmp, 'minion.pub')
    privkeyfn = os.path.join(tmp, 'minion.pem')
    with salt.utils.fopen(pubkeyfn) as fp_:
        pubkey = fp_.read()

    if approve_key:
        res = __salt__['pillar.ext']({'virtkey': [id_, pubkey]})
    res = _check_install(mpt)
    if res:
        # salt-minion is already installed, just move the config and keys
        # into place
        log.info('salt-minion pre-installed on image, '
                 'configuring as {0}'.format(id_))
        minion_config = salt.config.minion_config(tmp_config)
        pki_dir = minion_config['pki_dir']
        os.rename(privkeyfn, os.path.join(mpt,
                                          pki_dir.lstrip('/'),
                                          'minion.pem'))
        os.rename(pubkeyfn, os.path.join(mpt,
                                         pki_dir.lstrip('/'),
                                         'minion.pub'))
        os.rename(tmp_config, os.path.join(mpt, 'etc/salt/minion'))
    elif install:
        log.info('attempting to install salt-minion to '
                 '{0}'.format(mpt))
        res = _install(mpt)
    else:
        log.error('failed to configure salt-minion to '
                  '{0}'.format(mpt))
        res = False

    _umount(mpt, ftype)
    return res