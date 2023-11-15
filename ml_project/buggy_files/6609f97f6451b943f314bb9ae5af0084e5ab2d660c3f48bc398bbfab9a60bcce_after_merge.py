def get_matching_subnet(conn, module, vpc_id, cidr):
    filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id, 'cidr-block': cidr})
    try:
        subnets = get_subnet_info(conn.describe_subnets(Filters=filters))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get matching subnet")

    if len(subnets) > 0:
        return subnets[0]
    else:
        return None