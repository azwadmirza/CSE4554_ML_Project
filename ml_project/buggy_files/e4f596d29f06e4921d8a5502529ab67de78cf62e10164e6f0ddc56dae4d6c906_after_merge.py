def get_s3_bucket_list(boto3_session):
    client = boto3_session.client('s3')
    # NOTE no paginator available for this operation
    buckets = client.list_buckets()
    for bucket in buckets['Buckets']:
        bucket['Region'] = client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
    return buckets