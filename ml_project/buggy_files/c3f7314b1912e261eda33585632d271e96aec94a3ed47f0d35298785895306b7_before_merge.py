def _open_openml_url(openml_path, data_home):
    """
    Returns a resource from OpenML.org. Caches it to data_home if required.

    Parameters
    ----------
    openml_path : str
        OpenML URL that will be accessed. This will be prefixes with
        _OPENML_PREFIX

    data_home : str
        Directory to which the files will be cached. If None, no caching will
        be applied.

    Returns
    -------
    result : stream
        A stream to the OpenML resource
    """
    req = Request(_OPENML_PREFIX + openml_path)
    req.add_header('Accept-encoding', 'gzip')
    fsrc = urlopen(req)
    is_gzip = fsrc.info().get('Content-Encoding', '') == 'gzip'

    if data_home is None:
        if is_gzip:
            if PY2:
                fsrc = BytesIO(fsrc.read())
            return gzip.GzipFile(fileobj=fsrc, mode='rb')
        return fsrc

    local_path = os.path.join(data_home, 'openml.org', openml_path + ".gz")
    if not os.path.exists(local_path):
        try:
            os.makedirs(os.path.dirname(local_path))
        except OSError:
            # potentially, the directory has been created already
            pass

        try:
            with open(local_path, 'wb') as fdst:
                shutil.copyfileobj(fsrc, fdst)
                fsrc.close()
        except Exception:
            os.unlink(local_path)
            raise
    # XXX: unnecessary decompression on first access
    if is_gzip:
        return gzip.GzipFile(local_path, 'rb')
    return fsrc