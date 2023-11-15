def create_cluster(module, redshift):
    """
    Create a new cluster

    module: AnsibleModule object
    redshift: authenticated redshift connection object

    Returns:
    """

    identifier = module.params.get('identifier')
    node_type = module.params.get('node_type')
    username = module.params.get('username')
    password = module.params.get('password')
    d_b_name = module.params.get('db_name')
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')

    changed = True
    # Package up the optional parameters
    params = {}
    for p in ('cluster_type', 'cluster_security_groups',
              'vpc_security_group_ids', 'cluster_subnet_group_name',
              'availability_zone', 'preferred_maintenance_window',
              'cluster_parameter_group_name',
              'automated_snapshot_retention_period', 'port',
              'cluster_version', 'allow_version_upgrade',
              'number_of_nodes', 'publicly_accessible',
              'encrypted', 'elastic_ip', 'enhanced_vpc_routing'):
        # https://github.com/boto/boto3/issues/400
        if module.params.get(p) is not None:
            params[p] = module.params.get(p)

    if d_b_name:
        params['d_b_name'] = d_b_name

    try:
        redshift.describe_clusters(ClusterIdentifier=identifier)['Clusters'][0]
        changed = False
    except is_boto3_error_code('ClusterNotFound'):
        try:
            redshift.create_cluster(ClusterIdentifier=identifier,
                                    NodeType=node_type,
                                    MasterUsername=username,
                                    MasterUserPassword=password,
                                    **snake_dict_to_camel_dict(params, capitalize_first=True))
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            module.fail_json_aws(e, msg="Failed to create cluster")
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to describe cluster")
    if wait:
        attempts = wait_timeout // 60
        waiter = redshift.get_waiter('cluster_available')
        try:
            waiter.wait(
                ClusterIdentifier=identifier,
                WaiterConfig=dict(MaxAttempts=attempts)
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Timeout waiting for the cluster creation")
    try:
        resource = redshift.describe_clusters(ClusterIdentifier=identifier)['Clusters'][0]
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to describe cluster")

    return(changed, _collect_facts(resource))