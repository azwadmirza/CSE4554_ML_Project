def get_transit_gateways(boto3_session, region):
    client = boto3_session.client('ec2', region_name=region, config=get_botocore_config())
    return client.describe_transit_gateways()["TransitGateways"]