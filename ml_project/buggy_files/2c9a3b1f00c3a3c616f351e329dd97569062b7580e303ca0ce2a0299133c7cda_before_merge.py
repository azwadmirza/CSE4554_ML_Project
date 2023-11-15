def subnet_exists(conn, subnet_id):
    filters = ansible_dict_to_boto3_filter_list({'subnet-id': subnet_id})
    subnets = get_subnet_info(conn.describe_subnets(Filters=filters))
    if len(subnets) > 0 and 'state' in subnets[0] and subnets[0]['state'] == "available":
        return subnets[0]
    else:
        return False