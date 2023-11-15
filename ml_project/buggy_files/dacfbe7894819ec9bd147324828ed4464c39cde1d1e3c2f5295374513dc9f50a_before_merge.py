def find_subnets(connection, module, vpc_id, identified_subnets):
    """
    Finds a list of subnets, each identified either by a raw ID, a unique
    'Name' tag, or a CIDR such as 10.0.0.0/8.

    Note that this function is duplicated in other ec2 modules, and should
    potentially be moved into potentially be moved into a shared module_utils
    """
    subnet_ids = []
    subnet_names = []
    subnet_cidrs = []
    for subnet in (identified_subnets or []):
        if re.match(SUBNET_RE, subnet):
            subnet_ids.append(subnet)
        elif re.match(CIDR_RE, subnet):
            subnet_cidrs.append(subnet)
        else:
            subnet_names.append(subnet)

    subnets_by_id = []
    if subnet_ids:
        filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id})
        try:
            subnets_by_id = describe_subnets_with_backoff(connection, SubnetIds=subnet_ids, Filters=filters)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't find subnet with id %s" % subnet_ids)

    subnets_by_cidr = []
    if subnet_cidrs:
        filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id, 'cidr': subnet_cidrs})
        try:
            subnets_by_cidr = describe_subnets_with_backoff(connection, Filters=filters)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't find subnet with cidr %s" % subnet_cidrs)

    subnets_by_name = []
    if subnet_names:
        filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id, 'tag:Name': subnet_names})
        try:
            subnets_by_name = describe_subnets_with_backoff(connection, Filters=filters)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't find subnet with names %s" % subnet_names)

        for name in subnet_names:
            matching_count = len([1 for s in subnets_by_name if s.tags.get('Name') == name])
            if matching_count == 0:
                module.fail_json(msg='Subnet named "{0}" does not exist'.format(name))
            elif matching_count > 1:
                module.fail_json(msg='Multiple subnets named "{0}"'.format(name))

    return subnets_by_id + subnets_by_cidr + subnets_by_name