def path_to_url(path):
    """Convert a system path to a URL."""

    if os.path.sep == '/':
        return path

    if sys.version_info < (3, 0):
        path = path.encode('utf8')
    return pathname2url(path)