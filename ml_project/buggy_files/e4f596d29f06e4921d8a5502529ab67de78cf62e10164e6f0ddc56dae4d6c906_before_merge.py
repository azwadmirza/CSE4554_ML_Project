def get_s3_bucket_list(boto3_session):
    client = boto3_session.client('s3')
    # NOTE no paginator available for this operation
    return client.list_buckets()