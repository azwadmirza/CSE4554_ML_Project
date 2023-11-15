def get_policy(bucket, client):
    """
    Gets the S3 bucket policy. Returns policy string or None if no policy
    """
    try:
        policy = client.get_bucket_policy(Bucket=bucket['Name'])
    except ClientError as e:
        # no policy is defined for this bucket
        if "NoSuchBucketPolicy" in e.args[0]:
            policy = None
        elif "AccessDenied" in e.args[0]:
            logger.warning("Access denied trying to retrieve S3 bucket {} policy".format(bucket['Name']))
            policy = None
        elif "NoSuchBucket" in e.args[0]:
            logger.warning("get_bucket_policy({}) threw NoSuchBucket exception, skipping".format(bucket['Name']))
            policy = None
        elif "AllAccessDisabled" in e.args[0]:
            # Catches the following error : "An error occurred (AllAccessDisabled) when calling the
            # GetBucketAcl operation: All access to this object has been disabled"
            logger.warning("Failed to retrieve S3 bucket {} policies - Bucket is disabled".format(bucket['Name']))
            policy = None
        else:
            raise
    return policy