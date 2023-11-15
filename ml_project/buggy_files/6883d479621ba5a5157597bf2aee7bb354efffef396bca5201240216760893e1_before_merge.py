def find_address(ec2, module, public_ip, device_id, is_instance=True):
    """ Find an existing Elastic IP address """
    filters = []
    kwargs = {}

    if public_ip:
        kwargs["PublicIps"] = [public_ip]
    elif device_id:
        if is_instance:
            filters.append({"Name": 'instance-id', "Values": [device_id]})
        else:
            filters.append({'Name': 'network-interface-id', "Values": [device_id]})

    if len(filters) > 0:
        kwargs["Filters"] = filters
    elif len(filters) == 0 and public_ip is None:
        return None

    try:
        addresses = ec2.describe_addresses(**kwargs)
    except is_boto3_error_code('InvalidAddress.NotFound') as e:
        module.fail_json_aws(e, msg="Couldn't obtain list of existing Elastic IP addresses")

    addresses = addresses["Addresses"]
    if len(addresses) == 1:
        return addresses[0]
    elif len(addresses) > 1:
        msg = "Found more than one address using args {0}".format(kwargs)
        msg += "Addresses found: {0}".format(addresses)
        module.fail_json_aws(botocore.exceptions.ClientError, msg=msg)