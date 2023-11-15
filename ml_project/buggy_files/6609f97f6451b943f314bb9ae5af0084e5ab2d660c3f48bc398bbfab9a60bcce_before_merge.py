def get_matching_subnet(conn, vpc_id, cidr):
    filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id, 'cidr-block': cidr})
    subnets = get_subnet_info(conn.describe_subnets(Filters=filters))
    if len(subnets) > 0:
        return subnets[0]
    else:
        return None