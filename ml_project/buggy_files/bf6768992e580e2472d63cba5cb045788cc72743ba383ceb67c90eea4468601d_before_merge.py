def update():
    """
    Update the cache file for the bucket.
    """

    metadata = _init()

    if S3_SYNC_ON_UPDATE:
        # sync the buckets to the local cache
        log.info("Syncing local cache from S3...")
        for saltenv, env_meta in six.iteritems(metadata):
            for bucket_files in _find_files(env_meta):
                for bucket, files in six.iteritems(bucket_files):
                    for file_path in files:
                        cached_file_path = _get_cached_file_name(
                            bucket, saltenv, file_path
                        )
                        log.info("%s - %s : %s", bucket, saltenv, file_path)

                        # load the file from S3 if it's not in the cache or it's old
                        _get_file_from_s3(
                            metadata, saltenv, bucket, file_path, cached_file_path
                        )

        log.info("Sync local cache from S3 completed.")