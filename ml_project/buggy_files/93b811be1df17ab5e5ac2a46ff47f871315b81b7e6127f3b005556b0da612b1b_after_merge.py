def delete_bucket(module, s3, bucket):
    if module.check_mode:
        module.exit_json(msg="DELETE operation skipped - running in check mode", changed=True)
    try:
        bucket = s3.lookup(bucket, validate=False)
        bucket_contents = bucket.list()
        bucket.delete_keys([key.name for key in bucket_contents])
    except s3.provider.storage_response_error as e:
        if e.status == 404:
            # bucket doesn't appear to exist
            return False
        elif e.status == 403:
            # bucket appears to exist but user doesn't have list bucket permission; may still be able to delete bucket
            pass
        else:
            module.fail_json(msg=str(e), exception=traceback.format_exc())
    try:
        bucket.delete()
        return True
    except s3.provider.storage_response_error as e:
        if e.status == 403:
            module.exit_json(msg="Unable to complete DELETE operation. Check you have have s3:DeleteBucket "
                             "permission. Error: {0}.".format(e.message),
                             exception=traceback.format_exc())
        elif e.status == 409:
            module.exit_json(msg="Unable to complete DELETE operation. It appears there are contents in the "
                             "bucket that you don't have permission to delete. Error: {0}.".format(e.message),
                             exception=traceback.format_exc())
        else:
            module.fail_json(msg=str(e), exception=traceback.format_exc())