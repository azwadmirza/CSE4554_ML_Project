def get_elb_config(name, region=None, key=None, keyid=None, profile=None):
    '''
    Check to see if an ELB exists.

    CLI example:

    .. code-block:: bash

        salt myminion boto_elb.exists myelb region=us-east-1
    '''
    conn = _get_conn(region=region, key=key, keyid=keyid, profile=profile)

    try:
        lb = conn.get_all_load_balancers(load_balancer_names=[name])
        lb = lb[0]
        ret = {}
        ret['availability_zones'] = lb.availability_zones
        listeners = []
        for _listener in lb.listeners:
            listener_dict = {}
            listener_dict['elb_port'] = _listener.load_balancer_port
            listener_dict['elb_protocol'] = _listener.protocol
            listener_dict['instance_port'] = _listener.instance_port
            listener_dict['instance_protocol'] = _listener.instance_protocol
            listener_dict['policies'] = _listener.policy_names
            if _listener.ssl_certificate_id:
                listener_dict['certificate'] = _listener.ssl_certificate_id
            listeners.append(listener_dict)
        ret['listeners'] = listeners
        backends = []
        for _backend in lb.backends:
            bs_dict = {}
            bs_dict['instance_port'] = _backend.instance_port
            bs_dict['policies'] = [p.policy_name for p in _backend.policies]
            backends.append(bs_dict)
        ret['backends'] = backends
        ret['subnets'] = lb.subnets
        ret['security_groups'] = lb.security_groups
        ret['scheme'] = lb.scheme
        ret['dns_name'] = lb.dns_name
        ret['tags'] = _get_all_tags(conn, name)
        lb_policy_lists = [
            lb.policies.app_cookie_stickiness_policies,
            lb.policies.lb_cookie_stickiness_policies,
            lb.policies.other_policies
            ]
        policies = []
        for policy_list in lb_policy_lists:
            policies += [p.policy_name for p in policy_list]
        ret['policies'] = policies
        return ret
    except boto.exception.BotoServerError as error:
        log.debug(error)
        return {}