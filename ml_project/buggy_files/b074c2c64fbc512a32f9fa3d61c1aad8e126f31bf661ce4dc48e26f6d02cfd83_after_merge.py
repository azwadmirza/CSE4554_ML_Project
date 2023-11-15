def parse_path(path):
    """Parse a dataset's identifier or path into its parts

    Parameters
    ----------
    path : str or path-like object
        The path to be parsed.

    Returns
    -------
    ParsedPath or UnparsedPath

    Notes
    -----
    When legacy GDAL filenames are encountered, they will be returned
    in a UnparsedPath.
    """
    if isinstance(path, Path):
        return path

    # Windows drive letters (e.g. "C:\") confuse `urlparse` as they look like
    # URL schemes
    elif sys.platform == "win32" and re.match("^[a-zA-Z]\\:", path):
        return UnparsedPath(path)

    elif path.startswith('/vsi'):
        return UnparsedPath(path)

    elif re.match("^[a-z\\+]*://", path):
        parts = urlparse(path)

        # if the scheme is not one of Rasterio's supported schemes, we
        # return an UnparsedPath.
        if parts.scheme and not all(p in SCHEMES for p in parts.scheme.split('+')):
            return UnparsedPath(path)

        else:
            return ParsedPath.from_uri(path)
    
    else:
        return UnparsedPath(path)