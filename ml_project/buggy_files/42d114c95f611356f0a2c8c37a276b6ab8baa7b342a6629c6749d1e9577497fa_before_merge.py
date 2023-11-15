def find_file(path, saltenv="base", **kwargs):
    """
    Look through the buckets cache file for a match.
    If the field is found, it is retrieved from S3 only if its cached version
    is missing, or if the MD5 does not match.
    """
    if "env" in kwargs:
        # "env" is not supported; Use "saltenv".
        kwargs.pop("env")

    fnd = {"bucket": None, "path": None}

    metadata = _init()
    if not metadata or saltenv not in metadata:
        return fnd

    env_files = _find_files(metadata[saltenv])

    if not _is_env_per_bucket():
        path = os.path.join(saltenv, path)

    # look for the files and check if they're ignored globally
    for bucket in env_files:
        for bucket_name, files in six.iteritems(bucket):
            if path in files and not fs.is_file_ignored(__opts__, path):
                fnd["bucket"] = bucket_name
                fnd["path"] = path
                break
        else:
            continue  # only executes if we didn't break
        break

    if not fnd["path"] or not fnd["bucket"]:
        return fnd

    cached_file_path = _get_cached_file_name(fnd["bucket"], saltenv, path)

    # jit load the file from S3 if it's not in the cache or it's old
    _get_file_from_s3(metadata, saltenv, fnd["bucket"], path, cached_file_path)

    return fnd