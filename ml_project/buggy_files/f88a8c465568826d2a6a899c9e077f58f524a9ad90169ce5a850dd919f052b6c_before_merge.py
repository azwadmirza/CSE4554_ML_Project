def _get_file_from_s3(metadata, saltenv, bucket_name, path, cached_file_path):
    """
    Checks the local cache for the file, if it's old or missing go grab the
    file from S3 and update the cache
    """
    (
        key,
        keyid,
        service_url,
        verify_ssl,
        kms_keyid,
        location,
        path_style,
        https_enable,
    ) = _get_s3_key()

    # check the local cache...
    if os.path.isfile(cached_file_path):
        file_meta = _find_file_meta(metadata, bucket_name, saltenv, path)
        if file_meta:
            file_etag = file_meta["ETag"]

            if file_etag.find("-") == -1:
                file_md5 = file_etag
                cached_md5 = salt.utils.hashutils.get_hash(cached_file_path, "md5")

                # hashes match we have a cache hit
                if cached_md5 == file_md5:
                    return
            else:
                cached_file_stat = os.stat(cached_file_path)
                cached_file_size = cached_file_stat.st_size
                cached_file_mtime = datetime.datetime.fromtimestamp(
                    cached_file_stat.st_mtime
                )

                cached_file_lastmod = datetime.datetime.strptime(
                    file_meta["LastModified"], "%Y-%m-%dT%H:%M:%S.%fZ"
                )
                if (
                    cached_file_size == int(file_meta["Size"])
                    and cached_file_mtime > cached_file_lastmod
                ):
                    log.debug(
                        "cached file size equal to metadata size and "
                        "cached file mtime later than metadata last "
                        "modification time."
                    )
                    ret = __utils__["s3.query"](
                        key=key,
                        keyid=keyid,
                        kms_keyid=keyid,
                        method="HEAD",
                        bucket=bucket_name,
                        service_url=service_url,
                        verify_ssl=verify_ssl,
                        location=location,
                        path=_quote(path),
                        local_file=cached_file_path,
                        full_headers=True,
                        path_style=path_style,
                        https_enable=https_enable,
                    )
                    if ret is not None:
                        for header_name, header_value in ret["headers"].items():
                            name = header_name.strip()
                            value = header_value.strip()
                            if six.text_type(name).lower() == "last-modified":
                                s3_file_mtime = datetime.datetime.strptime(
                                    value, "%a, %d %b %Y %H:%M:%S %Z"
                                )
                            elif six.text_type(name).lower() == "content-length":
                                s3_file_size = int(value)
                        if (
                            cached_file_size == s3_file_size
                            and cached_file_mtime > s3_file_mtime
                        ):
                            log.info(
                                "%s - %s : %s skipped download since cached file size "
                                "equal to and mtime after s3 values",
                                bucket_name,
                                saltenv,
                                path,
                            )
                            return

    # ... or get the file from S3
    __utils__["s3.query"](
        key=key,
        keyid=keyid,
        kms_keyid=keyid,
        bucket=bucket_name,
        service_url=service_url,
        verify_ssl=verify_ssl,
        location=location,
        path=_quote(path),
        local_file=cached_file_path,
        path_style=path_style,
        https_enable=https_enable,
    )