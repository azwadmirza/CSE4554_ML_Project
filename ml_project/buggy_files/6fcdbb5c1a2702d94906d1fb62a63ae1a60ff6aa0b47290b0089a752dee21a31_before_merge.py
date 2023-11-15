def path_to_url(path):
    """Convert a system path to a URL."""

    if os.path.sep == '/':
        return path

    return pathname2url(path)