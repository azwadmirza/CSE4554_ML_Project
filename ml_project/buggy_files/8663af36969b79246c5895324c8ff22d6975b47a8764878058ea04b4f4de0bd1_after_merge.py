def ensure_subnet_absent(conn, module):
    subnet = get_matching_subnet(conn, module, module.params['vpc_id'], module.params['cidr'])
    if subnet is None:
        return {'changed': False}

    try:
        if not module.check_mode:
            conn.delete_subnet(SubnetId=subnet['id'])
            if module.params['wait']:
                handle_waiter(conn, module, 'subnet_deleted', {'SubnetIds': [subnet['id']]}, time.time())
        return {'changed': True}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete subnet")