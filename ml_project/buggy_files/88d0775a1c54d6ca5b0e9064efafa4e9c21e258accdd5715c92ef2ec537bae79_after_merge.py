def get_vpc(module, connection, vpc_id):
    # wait for vpc to be available
    try:
        connection.get_waiter('vpc_available').wait(VpcIds=[vpc_id])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Unable to wait for VPC {0} to be available.".format(vpc_id))

    try:
        vpc_obj = AWSRetry.backoff(
            delay=3, tries=8,
            catch_extra_error_codes=['InvalidVpcID.NotFound'],
        )(connection.describe_vpcs)(VpcIds=[vpc_id])['Vpcs'][0]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe VPCs")
    try:
        vpc_obj['ClassicLinkEnabled'] = get_classic_link_with_backoff(connection, vpc_id)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe VPCs")

    return vpc_obj