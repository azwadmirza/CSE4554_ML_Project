def action(*args, **kwargs):
    '''
    Execute a single action on the given map/provider/instance

    CLI Example:

    .. code-block:: bash

        salt-run cloud.actions start my-salt-vm
    '''
    client = _get_client()
    try:
        info = client.action(args[0],
                             kwargs.get('cloudmap', None),
                             args[1:],
                             kwargs.get('provider', None),
                             kwargs.get('instance', None),
                             kwargs)
    except SaltCloudConfigError as err:
        log.error(err)
        return {}

    return info