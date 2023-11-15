def delete_bucket(module, s3, bucket):
    if module.check_mode:
        module.exit_json(msg="DELETE operation skipped - running in check mode", changed=True)
    try:
        bucket = s3.lookup(bucket)
        bucket_contents = bucket.list()
        bucket.delete_keys([key.name for key in bucket_contents])
        bucket.delete()
        return True
    except s3.provider.storage_response_error as e:
        module.fail_json(msg= str(e))