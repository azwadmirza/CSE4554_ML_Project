def send_file(filename_or_fp, mimetype=None, as_attachment=False,
              attachment_filename=None, add_etags=True,
              cache_timeout=None, conditional=False, last_modified=None):
    """Sends the contents of a file to the client.  This will use the
    most efficient method available and configured.  By default it will
    try to use the WSGI server's file_wrapper support.  Alternatively
    you can set the application's :attr:`~Flask.use_x_sendfile` attribute
    to ``True`` to directly emit an ``X-Sendfile`` header.  This however
    requires support of the underlying webserver for ``X-Sendfile``.

    By default it will try to guess the mimetype for you, but you can
    also explicitly provide one.  For extra security you probably want
    to send certain files as attachment (HTML for instance).  The mimetype
    guessing requires a `filename` or an `attachment_filename` to be
    provided.

    ETags will also be attached automatically if a `filename` is provided. You
    can turn this off by setting `add_etags=False`.

    If `conditional=True` and `filename` is provided, this method will try to
    upgrade the response stream to support range requests.  This will allow
    the request to be answered with partial content response.

    Please never pass filenames to this function from user sources;
    you should use :func:`send_from_directory` instead.

    .. versionadded:: 0.2

    .. versionadded:: 0.5
       The `add_etags`, `cache_timeout` and `conditional` parameters were
       added.  The default behavior is now to attach etags.

    .. versionchanged:: 0.7
       mimetype guessing and etag support for file objects was
       deprecated because it was unreliable.  Pass a filename if you are
       able to, otherwise attach an etag yourself.  This functionality
       will be removed in Flask 1.0

    .. versionchanged:: 0.9
       cache_timeout pulls its default from application config, when None.

    .. versionchanged:: 0.12
       The filename is no longer automatically inferred from file objects. If
       you want to use automatic mimetype and etag support, pass a filepath via
       `filename_or_fp` or `attachment_filename`.

    .. versionchanged:: 0.12
       The `attachment_filename` is preferred over `filename` for MIME-type
       detection.

    :param filename_or_fp: the filename of the file to send in `latin-1`.
                           This is relative to the :attr:`~Flask.root_path`
                           if a relative path is specified.
                           Alternatively a file object might be provided in
                           which case ``X-Sendfile`` might not work and fall
                           back to the traditional method.  Make sure that the
                           file pointer is positioned at the start of data to
                           send before calling :func:`send_file`.
    :param mimetype: the mimetype of the file if provided. If a file path is
                     given, auto detection happens as fallback, otherwise an
                     error will be raised.
    :param as_attachment: set to ``True`` if you want to send this file with
                          a ``Content-Disposition: attachment`` header.
    :param attachment_filename: the filename for the attachment if it
                                differs from the file's filename.
    :param add_etags: set to ``False`` to disable attaching of etags.
    :param conditional: set to ``True`` to enable conditional responses.

    :param cache_timeout: the timeout in seconds for the headers. When ``None``
                          (default), this value is set by
                          :meth:`~Flask.get_send_file_max_age` of
                          :data:`~flask.current_app`.
    :param last_modified: set the ``Last-Modified`` header to this value,
        a :class:`~datetime.datetime` or timestamp.
        If a file was passed, this overrides its mtime.
    """
    mtime = None
    fsize = None
    if isinstance(filename_or_fp, string_types):
        filename = filename_or_fp
        if not os.path.isabs(filename):
            filename = os.path.join(current_app.root_path, filename)
        file = None
        if attachment_filename is None:
            attachment_filename = os.path.basename(filename)
    else:
        file = filename_or_fp
        filename = None

    if mimetype is None:
        if attachment_filename is not None:
            mimetype = mimetypes.guess_type(attachment_filename)[0] \
                or 'application/octet-stream'

        if mimetype is None:
            raise ValueError(
                'Unable to infer MIME-type because no filename is available. '
                'Please set either `attachment_filename`, pass a filepath to '
                '`filename_or_fp` or set your own MIME-type via `mimetype`.'
            )

    headers = Headers()
    if as_attachment:
        if attachment_filename is None:
            raise TypeError('filename unavailable, required for '
                            'sending as attachment')
        headers.add('Content-Disposition', 'attachment',
                    filename=attachment_filename)

    if current_app.use_x_sendfile and filename:
        if file is not None:
            file.close()
        headers['X-Sendfile'] = filename
        fsize = os.path.getsize(filename)
        headers['Content-Length'] = fsize
        data = None
    else:
        if file is None:
            file = open(filename, 'rb')
            mtime = os.path.getmtime(filename)
            fsize = os.path.getsize(filename)
            headers['Content-Length'] = fsize
        data = wrap_file(request.environ, file)

    rv = current_app.response_class(data, mimetype=mimetype, headers=headers,
                                    direct_passthrough=True)

    if last_modified is not None:
        rv.last_modified = last_modified
    elif mtime is not None:
        rv.last_modified = mtime

    rv.cache_control.public = True
    if cache_timeout is None:
        cache_timeout = current_app.get_send_file_max_age(filename)
    if cache_timeout is not None:
        rv.cache_control.max_age = cache_timeout
        rv.expires = int(time() + cache_timeout)

    if add_etags and filename is not None:
        from warnings import warn

        try:
            rv.set_etag('%s-%s-%s' % (
                os.path.getmtime(filename),
                os.path.getsize(filename),
                adler32(
                    filename.encode('utf-8') if isinstance(filename, text_type)
                    else filename
                ) & 0xffffffff
            ))
        except OSError:
            warn('Access %s failed, maybe it does not exist, so ignore etags in '
                 'headers' % filename, stacklevel=2)

    if conditional:
        if callable(getattr(Range, 'to_content_range_header', None)):
            # Werkzeug supports Range Requests
            # Remove this test when support for Werkzeug <0.12 is dropped
            try:
                rv = rv.make_conditional(request, accept_ranges=True,
                                         complete_length=fsize)
            except RequestedRangeNotSatisfiable:
                if file is not None:
                    file.close()
                raise
        else:
            rv = rv.make_conditional(request)
        # make sure we don't send x-sendfile for servers that
        # ignore the 304 status code for x-sendfile.
        if rv.status_code == 304:
            rv.headers.pop('x-sendfile', None)
    return rv