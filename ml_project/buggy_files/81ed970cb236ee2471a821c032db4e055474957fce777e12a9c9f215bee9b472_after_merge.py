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
    def is_gzip(_fsrc):
        return _fsrc.info().get('Content-Encoding', '') == 'gzip'

    req = Request(_OPENML_PREFIX + openml_path)
    req.add_header('Accept-encoding', 'gzip')

    if data_home is None:
        fsrc = urlopen(req)
        if is_gzip(fsrc):
            if PY2:
                fsrc = BytesIO(fsrc.read())
            return gzip.GzipFile(fileobj=fsrc, mode='rb')
        return fsrc

    local_path = _get_local_path(openml_path, data_home)
    if not os.path.exists(local_path):
        try:
            os.makedirs(os.path.dirname(local_path))
        except OSError:
            # potentially, the directory has been created already
            pass

        try:
            with closing(urlopen(req)) as fsrc:
                if is_gzip(fsrc):
                    with open(local_path, 'wb') as fdst:
                        shutil.copyfileobj(fsrc, fdst)
                else:
                    with gzip.GzipFile(local_path, 'wb') as fdst:
                        shutil.copyfileobj(fsrc, fdst)
        except Exception:
            if os.path.exists(local_path):
                os.unlink(local_path)
            raise

    # XXX: First time, decompression will not be necessary (by using fsrc), but
    # it will happen nonetheless
    return gzip.GzipFile(local_path, 'rb')