def securitygroupid(vm_):
    '''
    Returns the SecurityGroupId
    '''
    securitygroupid_set = set()
    securitygroupid_list = config.get_cloud_config_value(
        'securitygroupid', vm_, __opts__, search_global=False
    )
    # If the list is None, then the set will remain empty
    # If the list is already a set then calling 'set' on it is a no-op
    # If the list is a string, then calling 'set' generates a one-element set
    # If the list is anything else, stacktrace
    if securitygroupid_list:
        securitygroupid_set = securitygroupid_set.union(set(securitygroupid_list))

    securitygroupname_list = config.get_cloud_config_value(
        'securitygroupname', vm_, __opts__, search_global=False
    )
    if securitygroupname_list:
        if not isinstance(securitygroupname_list, list):
            securitygroupname_list = [securitygroupname_list]
        params = {'Action': 'DescribeSecurityGroups'}
        for sg in aws.query(params, location=get_location(),
                            provider=get_provider(), opts=__opts__, sigver='4'):
            if sg['groupName'] in securitygroupname_list:
                log.debug('AWS SecurityGroup ID of {0} is {1}'.format(
                    sg['groupName'], sg['groupId'])
                )
                securitygroupid_set = securitygroupid_set.add(sg['groupId'])
    return list(securitygroupid_set)