def create_lb(kwargs=None, call=None):
    r'''
    Create a load-balancer configuration.
    CLI Example:

    .. code-block:: bash

        salt-cloud -f create_lb dimensiondata \
            name=dev-lb port=80 protocol=http \
            members=w1,w2,w3 algorithm=ROUND_ROBIN
    '''
    conn = get_conn()
    if call != 'function':
        raise SaltCloudSystemExit(
            'The create_lb function must be called with -f or --function.'
        )

    if not kwargs or 'name' not in kwargs:
        log.error(
            'A name must be specified when creating a health check.'
        )
        return False
    if 'port' not in kwargs:
        log.error(
            'A port or port-range must be specified for the load-balancer.'
        )
        return False
    if 'networkdomain' not in kwargs:
        log.error(
            'A network domain must be specified for the load-balancer.'
        )
        return False
    if 'members' in kwargs:
        members = []
        ip = ""
        membersList = kwargs.get('members').split(',')
        log.debug('MemberList: %s', membersList)
        for member in membersList:
            try:
                log.debug('Member: %s', member)
                node = get_node(conn, member)
                log.debug('Node: %s', node)
                ip = node.private_ips[0]
            except Exception as err:
                log.error(
                    'Failed to get node ip: %s', err,
                    # Show the traceback if the debug logging level is enabled
                    exc_info_on_loglevel=logging.DEBUG
                )
            members.append(Member(ip, ip, kwargs['port']))
    else:
        members = None
    log.debug('Members: %s', members)

    networkdomain = kwargs['networkdomain']
    name = kwargs['name']
    port = kwargs['port']
    protocol = kwargs.get('protocol', None)
    algorithm = kwargs.get('algorithm', None)

    lb_conn = get_lb_conn(conn)
    network_domains = conn.ex_list_network_domains()
    network_domain = [y for y in network_domains if y.name == networkdomain][0]

    log.debug('Network Domain: %s', network_domain.id)
    lb_conn.ex_set_current_network_domain(network_domain.id)

    event_data = _to_event_data(kwargs)

    __utils__['cloud.fire_event'](
        'event',
        'create load_balancer',
        'salt/cloud/loadbalancer/creating',
        args=event_data,
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )

    lb = lb_conn.create_balancer(
        name, port, protocol, algorithm, members
    )

    event_data = _to_event_data(kwargs)

    __utils__['cloud.fire_event'](
        'event',
        'created load_balancer',
        'salt/cloud/loadbalancer/created',
        args=event_data,
        sock_dir=__opts__['sock_dir'],
        transport=__opts__['transport']
    )
    return _expand_balancer(lb)