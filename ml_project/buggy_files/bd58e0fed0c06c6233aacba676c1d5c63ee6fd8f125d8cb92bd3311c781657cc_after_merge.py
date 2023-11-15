def get_acl(bucket, client):
    """
    Gets the S3 bucket ACL. Returns ACL string
    """
    try:
        acl = client.get_bucket_acl(Bucket=bucket['Name'])
    except ClientError as e:
        if "AccessDenied" in e.args[0]:
            logger.warning("Failed to retrieve S3 bucket {} ACL - Access Denied".format(bucket['Name']))
            return None
        elif "NoSuchBucket" in e.args[0]:
            logger.warning("Failed to retrieve S3 bucket {} ACL - No Such Bucket".format(bucket['Name']))
            return None
        elif "AllAccessDisabled" in e.args[0]:
            logger.warning("Failed to retrieve S3 bucket {} ACL - Bucket is disabled".format(bucket['Name']))
            return None
        else:
            raise
    return acl