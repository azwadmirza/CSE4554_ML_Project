def ext_pillar(minion_id,
               pillar,  # pylint: disable=W0613
               bucket,
               key,
               keyid,
               verify_ssl=True,
               multiple_env=False,
               environment='base',
               prefix='',
               service_url=None):
    '''
    Execute a command and read the output as YAML
    '''

    s3_creds = S3Credentials(key, keyid, bucket, service_url, verify_ssl)

    # normpath is needed to remove appended '/' if root is empty string.
    pillar_dir = os.path.normpath(os.path.join(_get_cache_dir(), environment,
                                               bucket))
    if prefix:
        pillar_dir = os.path.normpath(os.path.join(pillar_dir, prefix))

    if __opts__['pillar_roots'].get(environment, []) == [pillar_dir]:
        return {}

    metadata = _init(s3_creds, bucket, multiple_env, environment, prefix)

    if _s3_sync_on_update:
        # sync the buckets to the local cache
        log.info('Syncing local pillar cache from S3...')
        for saltenv, env_meta in six.iteritems(metadata):
            for bucket, files in six.iteritems(_find_files(env_meta)):
                for file_path in files:
                    cached_file_path = _get_cached_file_name(bucket, saltenv,
                                                             file_path)
                    log.info('{0} - {1} : {2}'.format(bucket, saltenv,
                                                      file_path))
                    # load the file from S3 if not in the cache or too old
                    _get_file_from_s3(s3_creds, metadata, saltenv, bucket,
                                      file_path, cached_file_path)

        log.info('Sync local pillar cache from S3 completed.')

    opts = deepcopy(__opts__)
    opts['pillar_roots'][environment] = [pillar_dir]

    pil = Pillar(opts, __grains__, minion_id, environment)

    compiled_pillar = pil.compile_pillar()

    return compiled_pillar