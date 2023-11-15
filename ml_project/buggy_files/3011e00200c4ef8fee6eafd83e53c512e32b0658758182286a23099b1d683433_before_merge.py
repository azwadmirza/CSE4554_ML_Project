def _find_files(metadata):
    """
    Looks for all the files in the S3 bucket cache metadata
    """

    ret = []
    found = {}

    for bucket_dict in metadata:
        for bucket_name, data in six.iteritems(bucket_dict):
            filepaths = [k["Key"] for k in data]
            filepaths = [k for k in filepaths if not k.endswith("/")]
            if bucket_name not in found:
                found[bucket_name] = True
                ret.append({bucket_name: filepaths})
            else:
                for bucket in ret:
                    if bucket_name in bucket:
                        bucket[bucket_name] += filepaths
                        break
    return ret