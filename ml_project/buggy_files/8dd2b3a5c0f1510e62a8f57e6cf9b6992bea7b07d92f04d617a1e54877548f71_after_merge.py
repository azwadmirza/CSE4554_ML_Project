def get_s3_bucket_details(boto3_session, bucket_data):
    """
    Iterates over all S3 buckets. Yields bucket name (string) and pairs of S3 bucket policies (JSON) and ACLs (JSON)
    """
    # a local store for s3 clients so that we may re-use clients for an AWS region
    s3_regional_clients = {}

    for bucket in bucket_data['Buckets']:
        # Use us-east-1 region if no region was recognized for buckets
        # It was found that client.get_bucket_location does not return a region for buckets
        # in us-east-1 region
        client = s3_regional_clients.get(bucket['Region'])
        if(not client):
            client = boto3_session.client('s3', bucket['Region'])
            s3_regional_clients[bucket['Region']] = client
        acl = get_acl(bucket, client)
        policy = get_policy(bucket, client)
        yield bucket['Name'], acl, policy