def destroy(name, conn=None, call=None):
    '''
    Delete a single VM
    '''
    if call == 'function':
        raise SaltCloudSystemExit(
            'The destroy action must be called with -d, --destroy, '
            '-a or --action.'
        )

    salt.utils.cloud.fire_event(
        'event',
        'destroying instance',
        'salt/cloud/{0}/destroying'.format(name),
        {'name': name},
        transport=__opts__['transport']
    )

    if not conn:
        conn = get_conn()   # pylint: disable=E0602

    node = get_node(conn, name)
    profiles = get_configured_provider()['profiles']  # pylint: disable=E0602
    if node is None:
        log.error('Unable to find the VM {0}'.format(name))
    profile = None
    if 'metadata' in node.extra and 'profile' in node.extra['metadata']:
        profile = node.extra['metadata']['profile']
    flush_mine_on_destroy = False
    if profile is not None and profile in profiles:
        if 'flush_mine_on_destroy' in profiles[profile]:
            flush_mine_on_destroy = profiles[profile]['flush_mine_on_destroy']
    if flush_mine_on_destroy:
        log.info('Clearing Salt Mine: {0}'.format(name))
        client = salt.client.get_local_client(__opts__['conf_file'])
        minions = client.cmd(name, 'mine.flush')

    log.info('Clearing Salt Mine: {0}, {1}'.format(name, flush_mine_on_destroy))
    log.info('Destroying VM: {0}'.format(name))
    ret = conn.destroy_node(node)
    if ret:
        log.info('Destroyed VM: {0}'.format(name))
        # Fire destroy action
        salt.utils.cloud.fire_event(
            'event',
            'destroyed instance',
            'salt/cloud/{0}/destroyed'.format(name),
            {'name': name},
            transport=__opts__['transport']
        )
        if __opts__['delete_sshkeys'] is True:
            salt.utils.cloud.remove_sshkey(getattr(node, __opts__.get('ssh_interface', 'public_ips'))[0])
        if __opts__.get('update_cachedir', False) is True:
            salt.utils.cloud.delete_minion_cachedir(name, __active_provider_name__.split(':')[0], __opts__)

        return True

    log.error('Failed to Destroy VM: {0}'.format(name))
    return False