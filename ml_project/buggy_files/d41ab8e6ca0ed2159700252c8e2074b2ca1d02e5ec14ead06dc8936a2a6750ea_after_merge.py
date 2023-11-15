def _refresh_buckets_cache_file(cache_file):
    """
    Retrieve the content of all buckets and cache the metadata to the buckets
    cache file
    """

    log.debug("Refreshing buckets cache file")

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
    metadata = {}

    # helper s3 query function
    def __get_s3_meta(bucket, key=key, keyid=keyid):
        ret, marker = [], ""
        while True:
            tmp = __utils__["s3.query"](
                key=key,
                keyid=keyid,
                kms_keyid=keyid,
                bucket=bucket,
                service_url=service_url,
                verify_ssl=verify_ssl,
                location=location,
                return_bin=False,
                path_style=path_style,
                https_enable=https_enable,
                params={"marker": marker},
            )
            headers = []
            for header in tmp:
                if "Key" in header:
                    break
                headers.append(header)
            ret.extend(tmp)
            if all(
                [header.get("IsTruncated", "false") == "false" for header in headers]
            ):
                break
            marker = tmp[-1]["Key"]
        return ret

    if _is_env_per_bucket():
        # Single environment per bucket
        for saltenv, buckets in _get_buckets().items():
            bucket_files_list = []
            for bucket_name in buckets:
                bucket_files = {}
                s3_meta = __get_s3_meta(bucket_name)

                # s3 query returned nothing
                if not s3_meta:
                    continue

                # grab only the files/dirs
                bucket_files[bucket_name] = [k for k in s3_meta if "Key" in k]
                bucket_files_list.append(bucket_files)

                # check to see if we added any keys, otherwise investigate possible error conditions
                if not bucket_files[bucket_name]:
                    meta_response = {}
                    for k in s3_meta:
                        if "Code" in k or "Message" in k:
                            # assumes no duplicate keys, consisdent with current erro response.
                            meta_response.update(k)
                    # attempt use of human readable output first.
                    try:
                        log.warning(
                            "'%s' response for bucket '%s'",
                            meta_response["Message"],
                            bucket_name,
                        )
                        continue
                    except KeyError:
                        # no human readable error message provided
                        if "Code" in meta_response:
                            log.warning(
                                "'%s' response for bucket '%s'",
                                meta_response["Code"],
                                bucket_name,
                            )
                            continue
                        else:
                            log.warning(
                                "S3 Error! Do you have any files " "in your S3 bucket?"
                            )
                            return {}

            metadata[saltenv] = bucket_files_list

    else:
        # Multiple environments per buckets
        for bucket_name in _get_buckets():
            s3_meta = __get_s3_meta(bucket_name)

            # s3 query returned nothing
            if not s3_meta:
                continue

            # pull out the environment dirs (e.g. the root dirs)
            files = [k for k in s3_meta if "Key" in k]

            # check to see if we added any keys, otherwise investigate possible error conditions
            if not files:
                meta_response = {}
                for k in s3_meta:
                    if "Code" in k or "Message" in k:
                        # assumes no duplicate keys, consisdent with current erro response.
                        meta_response.update(k)
                # attempt use of human readable output first.
                try:
                    log.warning(
                        "'%s' response for bucket '%s'",
                        meta_response["Message"],
                        bucket_name,
                    )
                    continue
                except KeyError:
                    # no human readable error message provided
                    if "Code" in meta_response:
                        log.warning(
                            "'%s' response for bucket '%s'",
                            meta_response["Code"],
                            bucket_name,
                        )
                        continue
                    else:
                        log.warning(
                            "S3 Error! Do you have any files " "in your S3 bucket?"
                        )
                        return {}

            environments = [(os.path.dirname(k["Key"]).split("/", 1))[0] for k in files]
            environments = set(environments)

            # pull out the files for the environment
            for saltenv in environments:
                # grab only files/dirs that match this saltenv
                env_files = [k for k in files if k["Key"].startswith(saltenv)]

                if saltenv not in metadata:
                    metadata[saltenv] = []

                found = False
                for bucket_files in metadata[saltenv]:
                    if bucket_name in bucket_files:
                        bucket_files[bucket_name] += env_files
                        found = True
                        break
                if not found:
                    metadata[saltenv].append({bucket_name: env_files})

    # write the metadata to disk
    _write_buckets_cache_file(metadata, cache_file)

    return metadata