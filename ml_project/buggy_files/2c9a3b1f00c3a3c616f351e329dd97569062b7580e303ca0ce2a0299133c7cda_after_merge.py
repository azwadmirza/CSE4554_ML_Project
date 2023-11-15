def subnet_exists(conn, module, subnet_id):
    filters = ansible_dict_to_boto3_filter_list({'subnet-id': subnet_id})
    try:
        subnets = get_subnet_info(describe_subnets_with_backoff(conn, Filters=filters))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't check if subnet exists")
    if len(subnets) > 0 and 'state' in subnets[0] and subnets[0]['state'] == "available":
        return subnets[0]
    else:
        return False