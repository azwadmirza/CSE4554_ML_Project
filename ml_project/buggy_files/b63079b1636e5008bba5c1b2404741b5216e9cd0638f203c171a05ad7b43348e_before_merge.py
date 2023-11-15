def action(
        fun=None,
        cloudmap=None,
        names=None,
        provider=None,
        instance=None,
        **kwargs):
    '''
    Execute a single action on the given provider/instance

    CLI Example:

    .. code-block:: bash

        salt '*' cloud.action start instance=myinstance
        salt '*' cloud.action stop instance=myinstance
        salt '*' cloud.action show_image provider=my-ec2-config image=ami-1624987f
    '''
    client = _get_client()
    info = client.action(fun, cloudmap, names, provider, instance, kwargs)
    return info