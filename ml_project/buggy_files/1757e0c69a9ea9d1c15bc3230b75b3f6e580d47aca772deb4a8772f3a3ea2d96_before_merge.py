def _parse_uri(uri_as_string):
    """
    Parse the given URI from a string.

    Supported URI schemes are:

      * file
      * hdfs
      * http
      * https
      * s3
      * s3a
      * s3n
      * s3u
      * webhdfs

    .s3, s3a and s3n are treated the same way.  s3u is s3 but without SSL.

    Valid URI examples::

      * s3://my_bucket/my_key
      * s3://my_key:my_secret@my_bucket/my_key
      * s3://my_key:my_secret@my_server:my_port@my_bucket/my_key
      * hdfs:///path/file
      * hdfs://path/file
      * webhdfs://host:port/path/file
      * ./local/path/file
      * ~/local/path/file
      * local/path/file
      * ./local/path/file.gz
      * file:///home/user/file
      * file:///home/user/file.bz2
    """
    if os.name == 'nt':
        # urlsplit doesn't work on Windows -- it parses the drive as the scheme...
        if '://' not in uri_as_string:
            # no protocol given => assume a local file
            uri_as_string = 'file://' + uri_as_string
    parsed_uri = urlsplit(uri_as_string, allow_fragments=False)

    if parsed_uri.scheme == "hdfs":
        return _parse_uri_hdfs(parsed_uri)
    elif parsed_uri.scheme == "webhdfs":
        return _parse_uri_webhdfs(parsed_uri)
    elif parsed_uri.scheme in smart_open_s3.SUPPORTED_SCHEMES:
        return _parse_uri_s3x(parsed_uri)
    elif parsed_uri.scheme in ('file', '', None):
        return _parse_uri_file(parsed_uri)
    elif parsed_uri.scheme.startswith('http'):
        return Uri(scheme=parsed_uri.scheme, uri_path=uri_as_string)
    else:
        raise NotImplementedError(
            "unknown URI scheme %r in %r" % (parsed_uri.scheme, uri_as_string)
        )