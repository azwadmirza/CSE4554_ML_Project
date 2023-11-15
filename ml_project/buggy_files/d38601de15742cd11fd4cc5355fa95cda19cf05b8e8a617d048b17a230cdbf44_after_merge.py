def action(func=None,
           cloudmap=None,
           instances=None,
           provider=None,
           instance=None,
           **kwargs):
    '''
    Execute a single action on the given map/provider/instance

    CLI Example:

    .. code-block:: bash

        salt-run cloud.action start my-salt-vm
    '''
    info = {}
    client = _get_client()
    try:
        info = client.action(func, cloudmap, instances, provider, instance, **_filter_kwargs(kwargs))
    except SaltCloudConfigError as err:
        log.error(err)
    return info