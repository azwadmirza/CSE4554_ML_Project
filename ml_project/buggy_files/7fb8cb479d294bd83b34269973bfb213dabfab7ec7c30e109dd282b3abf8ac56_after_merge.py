def _open_binary_stream(uri, mode, transport_params):
    """Open an arbitrary URI in the specified binary mode.

    Not all modes are supported for all protocols.

    :arg uri: The URI to open.  May be a string, or something else.
    :arg str mode: The mode to open with.  Must be rb, wb or ab.
    :arg transport_params: Keyword argumens for the transport layer.
    :returns: A file object and the filename
    :rtype: tuple
    """
    if mode not in ('rb', 'rb+', 'wb', 'wb+', 'ab', 'ab+'):
        #
        # This should really be a ValueError, but for the sake of compatibility
        # with older versions, which raise NotImplementedError, we do the same.
        #
        raise NotImplementedError('unsupported mode: %r' % mode)

    if isinstance(uri, six.string_types):
        # this method just routes the request to classes handling the specific storage
        # schemes, depending on the URI protocol in `uri`
        filename = uri.split('/')[-1]
        parsed_uri = _parse_uri(uri)

        if parsed_uri.scheme == "file":
            fobj = io.open(parsed_uri.uri_path, mode)
            return fobj, filename
        elif parsed_uri.scheme in smart_open_ssh.SCHEMES:
            fobj = smart_open_ssh.open(
                parsed_uri.uri_path,
                mode,
                host=parsed_uri.host,
                user=parsed_uri.user,
                port=parsed_uri.port,
                password=parsed_uri.password,
                transport_params=transport_params,
            )
            return fobj, filename
        elif parsed_uri.scheme in smart_open_s3.SUPPORTED_SCHEMES:
            return _s3_open_uri(parsed_uri, mode, transport_params), filename
        elif parsed_uri.scheme == "hdfs":
            _check_kwargs(smart_open_hdfs.open, transport_params)
            return smart_open_hdfs.open(parsed_uri.uri_path, mode), filename
        elif parsed_uri.scheme == "webhdfs":
            kw = _check_kwargs(smart_open_webhdfs.open, transport_params)
            http_uri = smart_open_webhdfs.convert_to_http_uri(parsed_uri)
            return smart_open_webhdfs.open(http_uri, mode, **kw), filename
        elif parsed_uri.scheme.startswith('http'):
            #
            # The URI may contain a query string and fragments, which interfere
            # with our compressed/uncompressed estimation, so we strip them.
            #
            filename = P.basename(urlparse.urlparse(uri).path)
            kw = _check_kwargs(smart_open_http.open, transport_params)
            return smart_open_http.open(uri, mode, **kw), filename
        else:
            raise NotImplementedError("scheme %r is not supported", parsed_uri.scheme)
    elif hasattr(uri, 'read'):
        # simply pass-through if already a file-like
        # we need to return something as the file name, but we don't know what
        # so we probe for uri.name (e.g., this works with open() or tempfile.NamedTemporaryFile)
        # if the value ends with COMPRESSED_EXT, we will note it in _compression_wrapper()
        # if there is no such an attribute, we return "unknown" - this
        # effectively disables any compression
        filename = getattr(uri, 'name', 'unknown')
        return uri, filename
    else:
        raise TypeError("don't know how to handle uri %r" % uri)