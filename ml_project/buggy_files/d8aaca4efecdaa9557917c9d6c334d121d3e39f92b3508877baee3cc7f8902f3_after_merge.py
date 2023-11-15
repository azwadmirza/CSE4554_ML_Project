def get_transit_gateways(boto3_session, region):
    client = boto3_session.client('ec2', region_name=region, config=get_botocore_config())
    data = []
    try:
        data = client.describe_transit_gateways()["TransitGateways"]
    except botocore.exceptions.ClientError as e:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/error-handling.html#parsing-error-responses-and-catching-exceptions-from-aws-services
        logger.warning(
            "Could not retrieve Transit Gateways due to boto3 error %s: %s. Skipping.",
            e.response['Error']['Code'],
            e.response['Error']['Message'],
        )
    return data