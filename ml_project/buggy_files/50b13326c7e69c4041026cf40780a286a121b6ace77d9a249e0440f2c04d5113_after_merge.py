def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
        vpc_id=dict(type='str'),
        rules=dict(type='list'),
        rules_egress=dict(type='list'),
        state=dict(default='present', type='str', choices=['present', 'absent']),
        purge_rules=dict(default=True, required=False, type='bool'),
        purge_rules_egress=dict(default=True, required=False, type='bool'),

    )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    name = module.params['name']
    description = module.params['description']
    vpc_id = module.params['vpc_id']
    rules = deduplicate_rules_args(rules_expand_sources(rules_expand_ports(module.params['rules'])))
    rules_egress = deduplicate_rules_args(rules_expand_sources(rules_expand_ports(module.params['rules_egress'])))
    state = module.params.get('state')
    purge_rules = module.params['purge_rules']
    purge_rules_egress = module.params['purge_rules_egress']

    if state == 'present' and not description:
        module.fail_json(msg='Must provide description when state is present.')

    changed = False

    ec2 = ec2_connect(module)

    # find the group if present
    group = None
    groups = {}

    try:
        security_groups = ec2.get_all_security_groups()
    except BotoServerError as e:
        module.fail_json(msg="Error in get_all_security_groups: %s" % e.message, exception=traceback.format_exc())

    for curGroup in security_groups:
        groups[curGroup.id] = curGroup
        if curGroup.name in groups:
            # Prioritise groups from the current VPC
            if vpc_id is None or curGroup.vpc_id == vpc_id:
                groups[curGroup.name] = curGroup
        else:
            groups[curGroup.name] = curGroup

        if curGroup.name == name and (vpc_id is None or curGroup.vpc_id == vpc_id):
            group = curGroup

    # Ensure requested group is absent
    if state == 'absent':
        if group:
            # found a match, delete it
            try:
                if not module.check_mode:
                    group.delete()
            except BotoServerError as e:
                module.fail_json(msg="Unable to delete security group '%s' - %s" % (group, e.message), exception=traceback.format_exc())
            else:
                group = None
                changed = True
        else:
            # no match found, no changes required
            pass

    # Ensure requested group is present
    elif state == 'present':
        if group:
            # existing group
            if group.description != description:
                module.fail_json(msg="Group description does not match existing group. ec2_group does not support this case.")

        # if the group doesn't exist, create it now
        else:
            # no match found, create it
            if not module.check_mode:
                group = ec2.create_security_group(name, description, vpc_id=vpc_id)

                # When a group is created, an egress_rule ALLOW ALL
                # to 0.0.0.0/0 is added automatically but it's not
                # reflected in the object returned by the AWS API
                # call. We re-read the group for getting an updated object
                # amazon sometimes takes a couple seconds to update the security group so wait till it exists
                while len(ec2.get_all_security_groups(filters={'group_id': group.id})) == 0:
                    time.sleep(0.1)

                group = ec2.get_all_security_groups(group_ids=(group.id,))[0]
            changed = True
    else:
        module.fail_json(msg="Unsupported state requested: %s" % state)

    # create a lookup for all existing rules on the group
    if group:

        # Manage ingress rules
        groupRules = {}
        addRulesToLookup(group.rules, 'in', groupRules)

        # Now, go through all provided rules and ensure they are there.
        if rules is not None:
            for rule in rules:
                validate_rule(module, rule)

                group_id, ip, target_group_created = get_target_from_rule(module, ec2, rule, name, group, groups, vpc_id)
                if target_group_created:
                    changed = True

                if rule['proto'] in ('all', '-1', -1):
                    rule['proto'] = -1
                    rule['from_port'] = None
                    rule['to_port'] = None

                # Convert ip to list we can iterate over
                if not isinstance(ip, list):
                    ip = [ip]

                # If rule already exists, don't later delete it
                for thisip in ip:
                    ruleId = make_rule_key('in', rule, group_id, thisip)
                    if ruleId not in groupRules:
                        grantGroup = None
                        if group_id:
                            grantGroup = groups[group_id]

                        if not module.check_mode:
                            group.authorize(rule['proto'], rule['from_port'], rule['to_port'], thisip, grantGroup)
                        changed = True
                    else:
                        del groupRules[ruleId]

        # Finally, remove anything left in the groupRules -- these will be defunct rules
        if purge_rules:
            for (rule, grant) in groupRules.values():
                grantGroup = None
                if grant.group_id:
                    if grant.owner_id != group.owner_id:
                        # this is a foreign Security Group. Since you can't fetch it you must create an instance of it
                        group_instance = SecurityGroup(owner_id=grant.owner_id, name=grant.name, id=grant.group_id)
                        groups[grant.group_id] = group_instance
                        groups[grant.name] = group_instance
                    grantGroup = groups[grant.group_id]
                if not module.check_mode:
                    group.revoke(rule.ip_protocol, rule.from_port, rule.to_port, grant.cidr_ip, grantGroup)
                changed = True

        # Manage egress rules
        groupRules = {}
        addRulesToLookup(group.rules_egress, 'out', groupRules)

        # Now, go through all provided rules and ensure they are there.
        if rules_egress is not None:
            for rule in rules_egress:
                validate_rule(module, rule)

                group_id, ip, target_group_created = get_target_from_rule(module, ec2, rule, name, group, groups, vpc_id)
                if target_group_created:
                    changed = True

                if rule['proto'] in ('all', '-1', -1):
                    rule['proto'] = -1
                    rule['from_port'] = None
                    rule['to_port'] = None

                # Convert ip to list we can iterate over
                if not isinstance(ip, list):
                    ip = [ip]

                # If rule already exists, don't later delete it
                for thisip in ip:
                    ruleId = make_rule_key('out', rule, group_id, thisip)
                    if ruleId in groupRules:
                        del groupRules[ruleId]
                    # Otherwise, add new rule
                    else:
                        grantGroup = None
                        if group_id:
                            grantGroup = groups[group_id].id

                        if not module.check_mode:
                            ec2.authorize_security_group_egress(
                                group_id=group.id,
                                ip_protocol=rule['proto'],
                                from_port=rule['from_port'],
                                to_port=rule['to_port'],
                                src_group_id=grantGroup,
                                cidr_ip=thisip)
                        changed = True
        else:
            # when no egress rules are specified,
            # we add in a default allow all out rule, which was the
            # default behavior before egress rules were added
            default_egress_rule = 'out--1-None-None-None-0.0.0.0/0'
            if default_egress_rule not in groupRules:
                if not module.check_mode:
                    ec2.authorize_security_group_egress(
                        group_id=group.id,
                        ip_protocol=-1,
                        from_port=None,
                        to_port=None,
                        src_group_id=None,
                        cidr_ip='0.0.0.0/0'
                    )
                changed = True
            else:
                # make sure the default egress rule is not removed
                del groupRules[default_egress_rule]

        # Finally, remove anything left in the groupRules -- these will be defunct rules
        if purge_rules_egress:
            for (rule, grant) in groupRules.values():
                grantGroup = None
                if grant.group_id:
                    grantGroup = groups[grant.group_id].id
                if not module.check_mode:
                    ec2.revoke_security_group_egress(
                        group_id=group.id,
                        ip_protocol=rule.ip_protocol,
                        from_port=rule.from_port,
                        to_port=rule.to_port,
                        src_group_id=grantGroup,
                        cidr_ip=grant.cidr_ip)
                changed = True

    if group:
        module.exit_json(changed=changed, group_id=group.id)
    else:
        module.exit_json(changed=changed, group_id=None)