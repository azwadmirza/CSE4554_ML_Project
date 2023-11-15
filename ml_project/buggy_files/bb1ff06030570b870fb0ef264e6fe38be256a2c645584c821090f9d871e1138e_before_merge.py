def create_subnet(conn, module, vpc_id, cidr, ipv6_cidr=None, az=None):
    wait = module.params['wait']
    wait_timeout = module.params['wait_timeout']

    params = dict(VpcId=vpc_id,
                  CidrBlock=cidr)

    if ipv6_cidr:
        params['Ipv6CidrBlock'] = ipv6_cidr

    if az:
        params['AvailabilityZone'] = az

    try:
        subnet = get_subnet_info(conn.create_subnet(**params))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't create subnet")

    # Sometimes AWS takes its time to create a subnet and so using
    # new subnets's id to do things like create tags results in
    # exception.
    if wait and subnet.get('state') != 'available':
        delay = 5
        max_attempts = wait_timeout / delay
        waiter_config = dict(Delay=delay, MaxAttempts=max_attempts)
        waiter = conn.get_waiter('subnet_available')
        try:
            waiter.wait(SubnetIds=[subnet['id']], WaiterConfig=waiter_config)
            subnet['state'] = 'available'
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json(msg="Create subnet action timed out waiting for Subnet to become available.")

    return subnet