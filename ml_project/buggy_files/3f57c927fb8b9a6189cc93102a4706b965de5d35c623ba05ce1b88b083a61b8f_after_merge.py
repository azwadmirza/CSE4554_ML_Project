def ensure_subnet_absent(conn, module, vpc_id, cidr, check_mode):
    subnet = get_matching_subnet(conn, module, vpc_id, cidr)
    if subnet is None:
        return {'changed': False}

    try:
        if not check_mode:
            conn.delete_subnet(SubnetId=subnet['id'], DryRun=check_mode)
        return {'changed': True}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete subnet")