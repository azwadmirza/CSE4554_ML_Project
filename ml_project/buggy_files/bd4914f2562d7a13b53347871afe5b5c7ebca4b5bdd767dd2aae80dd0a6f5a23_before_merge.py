def associate_ip_and_device(ec2, module, address, private_ip_address, device_id, allow_reassociation, check_mode, is_instance=True):
    if address_is_associated_with_device(ec2, module, address, device_id, is_instance):
        return {'changed': False}

    # If we're in check mode, nothing else to do
    if not check_mode:
        if is_instance:
            try:
                params = dict(
                    InstanceId=device_id,
                    PrivateIpAddress=private_ip_address,
                    AllowReassociation=allow_reassociation,
                )
                if address.domain == "vpc":
                    params['AllocationId'] = address['AllocationId']
                else:
                    params['PublicIp'] = address['PublicIp']
                res = ec2.associate_address(**params)
            except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
                msg = "Couldn't associate Elastic IP address with instance '{0}'".format(device_id)
                module.fail_json_aws(e, msg=msg)
        else:
            params = dict(
                NetworkInterfaceId=device_id,
                AllocationId=address['AllocationId'],
                AllowReassociation=allow_reassociation,
            )

            if private_ip_address:
                params['PrivateIpAddress'] = private_ip_address

            try:
                res = ec2.associate_address(aws_retry=True, **params)
            except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
                msg = "Couldn't associate Elastic IP address with network interface '{0}'".format(device_id)
                module.fail_json_aws(e, msg=msg)
        if not res:
            module.fail_json_aws(e, msg='Association failed.')

    return {'changed': True}