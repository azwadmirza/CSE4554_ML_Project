def url_get(module, url, dest, use_proxy, last_mod_time, force, timeout=10, headers=None, tmp_dest=''):
    """
    Download data from the url and store in a temporary file.

    Return (tempfile, info about the request)
    """
    if module.check_mode:
        method = 'HEAD'
    else:
        method = 'GET'

    rsp, info = fetch_url(module, url, use_proxy=use_proxy, force=force, last_mod_time=last_mod_time, timeout=timeout, headers=headers, method=method)

    if info['status'] == 304:
        module.exit_json(url=url, dest=dest, changed=False, msg=info.get('msg', ''))

    # Exceptions in fetch_url may result in a status -1, the ensures a proper error to the user in all cases
    if info['status'] == -1:
        module.fail_json(msg=info['msg'], url=url, dest=dest)

    if info['status'] != 200 and not url.startswith('file:/') and not (url.startswith('ftp:/') and info.get('msg', '').startswith('OK')):
        module.fail_json(msg="Request failed", status_code=info['status'], response=info['msg'], url=url, dest=dest)

    # create a temporary file and copy content to do checksum-based replacement
    if tmp_dest:
        # tmp_dest should be an existing dir
        tmp_dest_is_dir = os.path.isdir(tmp_dest)
        if not tmp_dest_is_dir:
            if os.path.exists(tmp_dest):
                module.fail_json(msg="%s is a file but should be a directory." % tmp_dest)
            else:
                module.fail_json(msg="%s directory does not exist." % tmp_dest)
    else:
        tmp_dest = module.tmpdir

    fd, tempname = tempfile.mkstemp(dir=tmp_dest)

    f = os.fdopen(fd, 'wb')
    try:
        shutil.copyfileobj(rsp, f)
    except Exception as e:
        os.remove(tempname)
        module.fail_json(msg="failed to create temporary content file: %s" % to_native(e), exception=traceback.format_exc())
    f.close()
    rsp.close()
    return tempname, info