def create(client, subnet_id, allocation_id, client_token=None,
           wait=False, wait_timeout=0, if_exist_do_not_create=False,
           check_mode=False):
    """Create an Amazon NAT Gateway.
    Args:
        client (botocore.client.EC2): Boto3 client
        subnet_id (str): The subnet_id the nat resides in.
        allocation_id (str): The eip Amazon identifier.

    Kwargs:
        if_exist_do_not_create (bool): if a nat gateway already exists in this
            subnet, than do not create another one.
            default = False
        wait (bool): Wait for the nat to be in the deleted state before returning.
            default = False
        wait_timeout (int): Number of seconds to wait, until this timeout is reached.
            default = 0
        client_token (str):
            default = None

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-1234567'
        >>> allocation_id = 'eipalloc-1234567'
        >>> create(client, subnet_id, allocation_id, if_exist_do_not_create=True, wait=True, wait_timeout=500)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-123456789",
                "subnet_id": "subnet-1234567",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "55.55.55.55",
                        "network_interface_id": "eni-1234567",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-1234567"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-1234567"
            }
        ]

    Returns:
        Tuple (bool, str, list)
    """
    params = {
        'SubnetId': subnet_id,
        'AllocationId': allocation_id
    }
    request_time = datetime.datetime.utcnow()
    changed = False
    success = False
    token_provided = False
    err_msg = ""

    if client_token:
        token_provided = True
        params['ClientToken'] = client_token

    try:
        if not check_mode:
            result = camel_dict_to_snake_dict(client.create_nat_gateway(**params)["NatGateway"])
        else:
            result = DRY_RUN_GATEWAYS[0]
            result['create_time'] = datetime.datetime.utcnow()
            result['nat_gateway_addresses'][0]['Allocation_id'] = allocation_id
            result['subnet_id'] = subnet_id

        success = True
        changed = True
        create_time = result['create_time'].replace(tzinfo=None)
        if token_provided and (request_time > create_time):
            changed = False
        elif wait:
            success, err_msg, result = (
                wait_for_status(
                    client, wait_timeout, result['nat_gateway_id'], 'available',
                    check_mode=check_mode
                )
            )
            if success:
                err_msg = (
                    'NAT gateway {0} created'.format(result['nat_gateway_id'])
                )

    except botocore.exceptions.ClientError as e:
        if "IdempotentParameterMismatch" in e.message:
            err_msg = (
                'NAT Gateway does not support update and token has already been provided: ' + str(e)
            )
        else:
            err_msg = str(e)
        success = False
        changed = False
        result = None

    return success, changed, err_msg, result