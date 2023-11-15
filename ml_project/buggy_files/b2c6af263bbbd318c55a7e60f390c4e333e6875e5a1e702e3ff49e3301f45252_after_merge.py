def get_sts_client(session, region):
    """Get the AWS STS endpoint specific for the given region.

    Returns the global endpoint if region is not specified.

    For the list of regional endpoints, see https://amzn.to/2ohJgtR
    """
    if region and USE_STS_REGIONAL:
        endpoint_url = "https://sts.{}.amazonaws.com".format(region)
        region_name = region
    else:
        endpoint_url = "https://sts.amazonaws.com"
        region_name = None
    return session.client(
        'sts', endpoint_url=endpoint_url, region_name=region_name)