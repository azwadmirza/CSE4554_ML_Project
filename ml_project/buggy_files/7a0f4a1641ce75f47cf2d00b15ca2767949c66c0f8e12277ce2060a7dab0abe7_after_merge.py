def create_vpc(connection, module, cidr_block, tenancy):
    try:
        if not module.check_mode:
            vpc_obj = connection.create_vpc(CidrBlock=cidr_block, InstanceTenancy=tenancy)
        else:
            module.exit_json(changed=True)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Failed to create the VPC")

    # wait for vpc to exist
    try:
        connection.get_waiter('vpc_exists').wait(VpcIds=[vpc_obj['Vpc']['VpcId']])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Unable to wait for VPC {0} to be created.".format(vpc_obj['Vpc']['VpcId']))

    return vpc_obj['Vpc']['VpcId']