def create(vm_):
    '''
    Create a VM in Xen

    The configuration for this function is read from the profile settings.

    .. code-block:: bash

        salt-cloud -p some_profile xenvm01

    '''
    name = vm_['name']
    record = {}
    ret = {}

    # Since using "provider: <provider-engine>" is deprecated, alias provider
    # to use driver: "driver: <provider-engine>"
    if 'provider' in vm_:
        vm_['driver'] = vm_.pop('provider')

    # fire creating event
    __utils__['cloud.fire_event'](
        'event',
        'starting create',
        'salt/cloud/{0}/creating'.format(name),
        args={
            'name': name,
            'profile': vm_['profile'],
            'provider': vm_['driver'],
        },
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )
    log.debug('Adding %s to cloud cache.', name)
    __utils__['cloud.cachedir_index_add'](
        vm_['name'], vm_['profile'], 'xen', vm_['driver']
    )

    # connect to xen
    session = _get_session()

    # determine resource pool
    resource_pool = _determine_resource_pool(session, vm_)

    # determine storage repo
    storage_repo = _determine_storage_repo(session, resource_pool, vm_)

    # build VM
    image = vm_.get('image')
    clone = vm_.get('clone')
    if clone is None:
        clone = True
    log.debug('Clone: %s ', clone)

    # fire event to read new vm properties (requesting)
    __utils__['cloud.fire_event'](
        'event',
        'requesting instance',
        'salt/cloud/{0}/requesting'.format(name),
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    # create by cloning template
    if clone:
        _clone_vm(image, name, session)
    else:
        _copy_vm(image, name, session, storage_repo)

    # provision template to vm
    _provision_vm(name, session)
    vm = _get_vm(name, session)

    # start vm
    start(name, None, session)

    # get new VM
    vm = _get_vm(name, session)

    # wait for vm to report IP via guest tools
    _wait_for_ip(name, session)

    # set static IP if configured
    _set_static_ip(name, session, vm_)

    # if not deploying salt then exit
    deploy = vm_.get('deploy', True)
    log.debug('delopy is set to %s', deploy)
    if deploy:
        record = session.xenapi.VM.get_record(vm)
        if record is not None:
            _deploy_salt_minion(name, session, vm_)
    else:
        log.debug(
            'The Salt minion will not be installed, deploy: %s',
            vm_['deploy']
        )
    record = session.xenapi.VM.get_record(vm)
    ret = show_instance(name)
    ret.update({'extra': record})

    __utils__['cloud.fire_event'](
        'event',
        'created instance',
        'salt/cloud/{0}/created'.format(name),
        args={
            'name': name,
            'profile': vm_['profile'],
            'provider': vm_['driver'],
        },
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )
    return ret