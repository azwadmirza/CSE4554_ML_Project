def get_resources_vms(call=None, resFilter=None, includeConfig=True):
    '''
    Retrieve all VMs available on this environment

    CLI Example:

    .. code-block:: bash

        salt-cloud -f get_resources_vms my-proxmox-config
    '''

    timeoutTime = time.time() + 60
    while True:
        log.debug('Getting resource: vms.. (filter: %s)', resFilter)
        resources = query('get', 'cluster/resources')
        ret = {}
        badResource = False
        for resource in resources:
            if 'type' in resource and resource['type'] in ['openvz', 'qemu',
                                                           'lxc']:
                try:
                    name = resource['name']
                except KeyError:
                    badResource = True
                    log.debug('No name in VM resource %s', repr(resource))
                    break

                ret[name] = resource

                if includeConfig:
                    # Requested to include the detailed configuration of a VM
                    ret[name]['config'] = get_vmconfig(
                        ret[name]['vmid'],
                        ret[name]['node'],
                        ret[name]['type']
                    )

        if time.time() > timeoutTime:
            raise SaltCloudExecutionTimeout('FAILED to get the proxmox '
                                            'resources vms')

        # Carry on if there wasn't a bad resource return from Proxmox
        if not badResource:
            break

        time.sleep(0.5)

    if resFilter is not None:
        log.debug('Filter given: %s, returning requested '
                  'resource: nodes', resFilter)
        return ret[resFilter]

    log.debug('Filter not given: %s, returning all resource: nodes', ret)
    return ret