def detect_phantomjs(version: str = '2.1') -> str:
    ''' Detect if PhantomJS is avaiable in PATH, at a minimum version.

    Args:
        version (str, optional) :
            Required minimum version for PhantomJS (mostly for testing)

    Returns:
        str, path to PhantomJS

    '''
    if settings.phantomjs_path() is not None:
        phantomjs_path = settings.phantomjs_path()
    else:
        phantomjs_path = shutil.which("phantomjs") or "phantomjs"

    try:
        proc = Popen([phantomjs_path, "--version"], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        proc.wait()
        out = proc.communicate()

        if len(out[1]) > 0:
            raise RuntimeError('Error encountered in PhantomJS detection: %r' % out[1].decode('utf8'))

        required = V(version)
        installed = V(out[0].decode('utf8'))
        if installed < required:
            raise RuntimeError('PhantomJS version to old. Version>=%s required, installed: %s' % (required, installed))

    except OSError:
        raise RuntimeError('PhantomJS is not present in PATH or BOKEH_PHANTOMJS_PATH. Try "conda install phantomjs" or \
            "npm install -g phantomjs-prebuilt"')

    return phantomjs_path