def _find_dirs(metadata):
    """
    Looks for all the directories in the S3 bucket cache metadata.

    Supports trailing '/' keys (as created by S3 console) as well as
    directories discovered in the path of file keys.
    """

    ret = []
    found = {}

    for bucket_dict in metadata:
        for bucket_name, data in six.iteritems(bucket_dict):
            dirpaths = set()
            for path in [k["Key"] for k in data]:
                prefix = ""
                for part in path.split("/")[:-1]:
                    directory = prefix + part + "/"
                    dirpaths.add(directory)
                    prefix = directory
            if bucket_name not in found:
                found[bucket_name] = True
                ret.append({bucket_name: list(dirpaths)})
            else:
                for bucket in ret:
                    if bucket_name in bucket:
                        bucket[bucket_name] += list(dirpaths)
                        bucket[bucket_name] = list(set(bucket[bucket_name]))
                        break
    return ret