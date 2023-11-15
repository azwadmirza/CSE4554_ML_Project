def unpack_http_url(link, location, download_cache, download_dir=None):
    temp_dir = tempfile.mkdtemp('-unpack', 'pip-')
    target_url = link.url.split('#', 1)[0]
    target_file = None
    download_hash = None
    if download_cache:
        target_file = os.path.join(download_cache,
                                   urllib.quote(target_url, ''))
        if not os.path.isdir(download_cache):
            create_download_cache_folder(download_cache)

    already_downloaded = None
    if download_dir:
        already_downloaded = os.path.join(download_dir, link.filename)
        if not os.path.exists(already_downloaded):
            already_downloaded = None

    if (target_file
        and os.path.exists(target_file)
        and os.path.exists(target_file + '.content-type')):
        fp = open(target_file+'.content-type')
        content_type = fp.read().strip()
        fp.close()
        if link.hash and link.hash_name:
            download_hash = _get_hash_from_file(target_file, link)
        temp_location = target_file
        logger.notify('Using download cache from %s' % target_file)
    elif already_downloaded:
        temp_location = already_downloaded
        content_type = mimetypes.guess_type(already_downloaded)
        if link.hash:
            download_hash = _get_hash_from_file(temp_location, link)
        logger.notify('File was already downloaded %s' % already_downloaded)
    else:
        resp = _get_response_from_url(target_url, link)
        content_type = resp.info()['content-type']
        filename = link.filename  # fallback
        # Have a look at the Content-Disposition header for a better guess
        content_disposition = resp.info().get('content-disposition')
        if content_disposition:
            type, params = cgi.parse_header(content_disposition)
            # We use ``or`` here because we don't want to use an "empty" value
            # from the filename param.
            filename = params.get('filename') or filename
        ext = splitext(filename)[1]
        if not ext:
            ext = mimetypes.guess_extension(content_type)
            if ext:
                filename += ext
        if not ext and link.url != geturl(resp):
            ext = os.path.splitext(geturl(resp))[1]
            if ext:
                filename += ext
        temp_location = os.path.join(temp_dir, filename)
        download_hash = _download_url(resp, link, temp_location)
    if link.hash and link.hash_name:
        _check_hash(download_hash, link)
    if download_dir and not already_downloaded:
        _copy_file(temp_location, download_dir, content_type, link)
    unpack_file(temp_location, location, content_type, link)
    if target_file and target_file != temp_location:
        cache_download(target_file, temp_location, content_type)
    if target_file is None and not already_downloaded:
        os.unlink(temp_location)
    os.rmdir(temp_dir)