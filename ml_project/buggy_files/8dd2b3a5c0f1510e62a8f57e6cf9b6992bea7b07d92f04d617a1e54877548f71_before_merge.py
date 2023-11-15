def get_s3_bucket_details(boto3_session, bucket_data):
    """
    Iterates over all S3 buckets. Yields bucket name (string) and pairs of S3 bucket policies (JSON) and ACLs (JSON)
    """
    client = boto3_session.client('s3')
    for bucket in bucket_data['Buckets']:
        acl = get_acl(bucket, client)
        policy = get_policy(bucket, client)
        yield bucket['Name'], acl, policy