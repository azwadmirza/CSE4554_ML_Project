def modify_cluster(module, redshift):
    """
    Modify an existing cluster.

    module: Ansible module object
    redshift: authenticated redshift connection object
    """

    identifier = module.params.get('identifier')
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')

    # Package up the optional parameters
    params = {}
    for p in ('cluster_type', 'cluster_security_groups',
              'vpc_security_group_ids', 'cluster_subnet_group_name',
              'availability_zone', 'preferred_maintenance_window',
              'cluster_parameter_group_name',
              'automated_snapshot_retention_period', 'port', 'cluster_version',
              'allow_version_upgrade', 'number_of_nodes', 'new_cluster_identifier'):
        # https://github.com/boto/boto3/issues/400
        if module.params.get(p) is not None:
            params[p] = module.params.get(p)

    # enhanced_vpc_routing parameter change needs an exclusive request
    if module.params.get('enhanced_vpc_routing') is not None:
        try:
            redshift.modify_cluster(ClusterIdentifier=identifier,
                                    EnhancedVpcRouting=module.params.get('enhanced_vpc_routing'))
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            module.fail_json_aws(e, msg="Couldn't modify redshift cluster %s " % identifier)
    if wait:
        attempts = wait_timeout // 60
        waiter = redshift.get_waiter('cluster_available')
        try:
            waiter.wait(
                ClusterIdentifier=identifier,
                WaiterConfig=dict(MaxAttempts=attempts)
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e,
                                 msg="Timeout waiting for cluster enhanced vpc routing modification"
                                 )

    # change the rest
    try:
        redshift.modify_cluster(ClusterIdentifier=identifier,
                                **snake_dict_to_camel_dict(params, capitalize_first=True))
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't modify redshift cluster %s " % identifier)

    if module.params.get('new_cluster_identifier'):
        identifier = module.params.get('new_cluster_identifier')

    if wait:
        attempts = wait_timeout // 60
        waiter2 = redshift.get_waiter('cluster_available')
        try:
            waiter2.wait(
                ClusterIdentifier=identifier,
                WaiterConfig=dict(MaxAttempts=attempts)
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Timeout waiting for cluster modification")
    try:
        resource = redshift.describe_clusters(ClusterIdentifier=identifier)['Clusters'][0]
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json(e, msg="Couldn't modify redshift cluster %s " % identifier)

    return(True, _collect_facts(resource))