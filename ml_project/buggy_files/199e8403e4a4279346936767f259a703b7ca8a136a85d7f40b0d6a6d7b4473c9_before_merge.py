def get_tgw_vpc_attachments(boto3_session, region):
    client = boto3_session.client('ec2', region_name=region, config=get_botocore_config())
    paginator = client.get_paginator('describe_transit_gateway_vpc_attachments')
    tgw_vpc_attachments = []
    for page in paginator.paginate():
        tgw_vpc_attachments.extend(page['TransitGatewayVpcAttachments'])
    return tgw_vpc_attachments