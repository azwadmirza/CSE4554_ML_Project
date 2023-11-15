def show_instance(name, conn=None, call=None):
    '''
    Get VM on this OpenStack account

    name

        name of the instance

    CLI Example

    .. code-block:: bash

        salt-cloud -a show_instance myserver

    '''
    if call != 'action':
        raise SaltCloudSystemExit(
            'The show_instance action must be called with -a or --action.'
        )
    if conn is None:
        conn = get_conn()

    node = conn.get_server(name, bare=True)
    ret = dict(node)
    ret['id'] = node.id
    ret['name'] = node.name
    ret['size'] = conn.get_flavor(node.flavor.id).name
    ret['state'] = node.status
    ret['private_ips'] = _get_ips(node, 'private')
    ret['public_ips'] = _get_ips(node, 'public')
    ret['floating_ips'] = _get_ips(node, 'floating')
    ret['fixed_ips'] = _get_ips(node, 'fixed')
    ret['image'] = conn.get_image(node.image.id).name
    return ret