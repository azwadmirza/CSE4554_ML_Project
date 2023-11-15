def get_tgw_attachments(boto3_session, region):
    client = boto3_session.client('ec2', region_name=region, config=get_botocore_config())
    paginator = client.get_paginator('describe_transit_gateway_attachments')
    tgw_attachments = []
    for page in paginator.paginate():
        tgw_attachments.extend(page['TransitGatewayAttachments'])
    return tgw_attachments