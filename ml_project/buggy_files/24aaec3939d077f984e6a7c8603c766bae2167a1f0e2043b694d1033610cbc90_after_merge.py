def _my_urlsplit(url):
    """This is a hack to prevent the regular urlsplit from splitting around question marks.

    A question mark (?) in a URL typically indicates the start of a
    querystring, and the standard library's urlparse function handles the
    querystring separately.  Unfortunately, question marks can also appear
    _inside_ the actual URL for some schemas like S3.

    Replaces question marks with newlines prior to splitting.  This is safe because:

    1. The standard library's urlsplit completely ignores newlines
    2. Raw newlines will never occur in innocuous URLs.  They are always URL-encoded.

    See Also
    --------
    https://github.com/python/cpython/blob/3.7/Lib/urllib/parse.py
    https://github.com/RaRe-Technologies/smart_open/issues/285
    """
    parsed_url = urlparse.urlsplit(url, allow_fragments=False)
    if parsed_url.scheme not in smart_open_s3.SUPPORTED_SCHEMES or '?' not in url:
        return parsed_url

    sr = urlparse.urlsplit(url.replace('?', '\n'), allow_fragments=False)
    return urlparse.SplitResult(sr.scheme, sr.netloc, sr.path.replace('\n', '?'), '', '')