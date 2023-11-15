def list_nodes(full=False, call=None):
    '''
    list of nodes, keeping only a brief listing

    CLI Example:

    .. code-block:: bash

        salt-cloud -Q
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The list_nodes function must be called with -f or --function.'
        )

    ret = {}
    if POLL_ALL_LOCATIONS:
        for location in JOYENT_LOCATIONS:
            result = query(command='my/machines', location=location,
                           method='GET')
            if result[0] in VALID_RESPONSE_CODES:
                nodes = result[1]
                for node in nodes:
                    if 'name' in node:
                        node['location'] = location
                        ret[node['name']] = reformat_node(item=node, full=full)
            else:
                log.error('Invalid response when listing Joyent nodes: {0}'.format(result[1]))

    else:
        result = query(command='my/machines', location=DEFAULT_LOCATION,
                       method='GET')
        nodes = result[1]
        for node in nodes:
            if 'name' in node:
                node['location'] = DEFAULT_LOCATION
                ret[node['name']] = reformat_node(item=node, full=full)
    return ret