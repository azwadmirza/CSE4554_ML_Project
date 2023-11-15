    def __init__(self, env, options=None):
        global _maybe_wrap_wsgi_stream

        self.env = env
        self.options = options if options else RequestOptions()

        if self.context_type is None:
            # Literal syntax is more efficient than using dict()
            self.context = {}
        else:
            # pylint will detect this as not-callable because it only sees the
            # declaration of None, not whatever type a subclass may have set.
            self.context = self.context_type()  # pylint: disable=not-callable

        self._wsgierrors = env['wsgi.errors']
        self.stream = env['wsgi.input']
        self.method = env['REQUEST_METHOD']

        # Normalize path
        path = env['PATH_INFO']
        if path:
            if six.PY3:  # pragma: no cover
                # PEP 3333 specifies that PATH_INFO variable are always
                # "bytes tunneled as latin-1" and must be encoded back
                path = path.encode('latin1').decode('utf-8', 'replace')

            if len(path) != 1 and path.endswith('/'):
                self.path = path[:-1]
            else:
                self.path = path
        else:
            self.path = '/'

        # PERF(kgriffs): if...in is faster than using env.get(...)
        if 'QUERY_STRING' in env:
            self.query_string = env['QUERY_STRING']

            if self.query_string:
                self._params = parse_query_string(
                    self.query_string,
                    keep_blank_qs_values=self.options.keep_blank_qs_values,
                )

            else:
                self._params = {}

        else:
            self.query_string = ''
            self._params = {}

        self._cookies = None

        self._cached_headers = None
        self._cached_uri = None
        self._cached_relative_uri = None

        try:
            self.content_type = self.env['CONTENT_TYPE']
        except KeyError:
            self.content_type = None

        # NOTE(kgriffs): Wrap wsgi.input if needed to make read() more robust,
        # normalizing semantics between, e.g., gunicorn and wsgiref.
        if _maybe_wrap_wsgi_stream:
            if isinstance(self.stream, NativeStream):
                # NOTE(kgriffs): This is covered by tests, it's just that
                # coverage can't figure this out for some reason (TBD).
                self._wrap_stream()  # pragma nocover
            else:
                # PERF(kgriffs): If self.stream does not need to be wrapped
                # this time, it never needs to be wrapped since the server
                # will continue using the same type for wsgi.input.
                _maybe_wrap_wsgi_stream = False

        # PERF(kgriffs): Technically, we should spend a few more
        # cycles and parse the content type for real, but
        # this heuristic will work virtually all the time.
        if (self.content_type is not None and
                'application/x-www-form-urlencoded' in self.content_type):
            self._parse_form_urlencoded()