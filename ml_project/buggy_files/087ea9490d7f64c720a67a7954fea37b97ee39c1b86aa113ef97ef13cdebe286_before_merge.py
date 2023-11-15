def _get_rule_changes(rules, _rules):
    '''
    given a list of desired rules (rules) and existing rules (_rules) return
    a list of rules to delete (to_delete) and to create (to_create)
    '''
    to_delete = []
    to_create = []
    # for each rule in state file
    # 1. validate rule
    # 2. determine if rule exists in existing security group rules
    for rule in rules:
        try:
            ip_protocol = rule.get('ip_protocol')
        except KeyError:
            raise SaltInvocationError('ip_protocol, to_port, and from_port are'
                                      ' required arguments for security group'
                                      ' rules.')
        supported_protocols = ['tcp', 'udp', 'icmp', 'all', '-1']
        if ip_protocol not in supported_protocols and (not ip_protocol.isdigit() or int(ip_protocol) > 255):
            msg = ('Invalid ip_protocol {0} specified in security group rule.')
            raise SaltInvocationError(msg.format(ip_protocol))
        # For the 'all' case, we need to change the protocol name to '-1'.
        if ip_protocol == 'all':
            rule['ip_protocol'] = '-1'
        cidr_ip = rule.get('cidr_ip', None)
        group_name = rule.get('source_group_name', None)
        group_id = rule.get('source_group_group_id', None)
        if cidr_ip and (group_id or group_name):
            raise SaltInvocationError('cidr_ip and source groups can not both'
                                      ' be specified in security group rules.')
        if group_id and group_name:
            raise SaltInvocationError('Either source_group_group_id or'
                                      ' source_group_name can be specified in'
                                      ' security group rules, but not both.')
        if not (cidr_ip or group_id or group_name):
            raise SaltInvocationError('cidr_ip, source_group_group_id, or'
                                      ' source_group_name must be provided for'
                                      ' security group rules.')
        rule_found = False
        # for each rule in existing security group ruleset determine if
        # new rule exists
        for _rule in _rules:
            if _check_rule(rule, _rule):
                rule_found = True
                break
        if not rule_found:
            to_create.append(rule)
    # for each rule in existing security group configuration
    # 1. determine if rules needed to be deleted
    for _rule in _rules:
        rule_found = False
        for rule in rules:
            if _check_rule(rule, _rule):
                rule_found = True
                break
        if not rule_found:
            # Can only supply name or id, not both. Since we're deleting
            # entries, it doesn't matter which we pick.
            _rule.pop('source_group_name', None)
            to_delete.append(_rule)
    log.debug('Rules to be deleted: {0}'.format(to_delete))
    log.debug('Rules to be created: {0}'.format(to_create))
    return (to_delete, to_create)