def copyKeyMultipart(srcKey, dstBucketName, dstKeyName, headers=None):
    """
    Copies a key from a source key to a destination key in multiple parts. Note that if the
    destination key exists it will be overwritten implicitly, and if it does not exist a new
    key will be created.

    :param boto.s3.key.Key srcKey: The source key to be copied from.
    :param str dstBucketName: The name of the destination bucket for the copy.
    :param str dstKeyName: The name of the destination key that will be created or overwritten.
    :param dict headers: Any headers that should be passed.

    :rtype: boto.s3.multipart.CompletedMultiPartUpload
    :return: An object representing the completed upload.
    """
    partSize = defaultPartSize
    s3 = boto.connect_s3()
    headers = headers or {}
    totalSize = srcKey.size

    # initiate copy
    upload = s3.get_bucket(dstBucketName).initiate_multipart_upload(dstKeyName, headers=headers)
    try:
        start = 0
        partIndex = itertools.count()
        while start < totalSize:
            end = min(start + partSize, totalSize)
            upload.copy_part_from_key(src_bucket_name=srcKey.bucket.name,
                                      src_key_name=srcKey.name,
                                      part_num=next(partIndex)+1,
                                      start=start,
                                      end=end-1,
                                      headers=headers)
            start += partSize
    except:
        upload.cancel_upload()
        raise
    else:
        return upload.complete_upload()