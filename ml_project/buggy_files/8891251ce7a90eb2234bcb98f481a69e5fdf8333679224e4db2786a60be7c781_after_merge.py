def delete_cluster(module, redshift):
    """
    Delete a cluster.

    module: Ansible module object
    redshift: authenticated redshift connection object
    """

    identifier = module.params.get('identifier')
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')

    params = {}
    for p in ('skip_final_cluster_snapshot',
              'final_cluster_snapshot_identifier'):
        if p in module.params:
            # https://github.com/boto/boto3/issues/400
            if module.params.get(p) is not None:
                params[p] = module.params.get(p)

    try:
        redshift.delete_cluster(
            ClusterIdentifier=identifier,
            **snake_dict_to_camel_dict(params, capitalize_first=True)
        )
    except is_boto3_error_code('ClusterNotFound'):
        return(False, {})
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to delete cluster")

    if wait:
        attempts = wait_timeout // 60
        waiter = redshift.get_waiter('cluster_deleted')
        try:
            waiter.wait(
                ClusterIdentifier=identifier,
                WaiterConfig=dict(MaxAttempts=attempts)
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Timeout deleting the cluster")

    return(True, {})