def get_tgw_attachments(boto3_session, region):
    client = boto3_session.client('ec2', region_name=region, config=get_botocore_config())
    tgw_attachments = []
    try:
        paginator = client.get_paginator('describe_transit_gateway_attachments')
        for page in paginator.paginate():
            tgw_attachments.extend(page['TransitGatewayAttachments'])
    except botocore.exceptions.ClientError as e:
        logger.warning(
            "Could not retrieve Transit Gateway Attachments due to boto3 error %s: %s. Skipping.",
            e.response['Error']['Code'],
            e.response['Error']['Message'],
        )
    return tgw_attachments