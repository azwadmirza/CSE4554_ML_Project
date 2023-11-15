    def __call__(self, environ, start_response):
        # type: (Dict[str, str], Callable[..., Any]) -> _ScopedResponse
        if _wsgi_middleware_applied.get(False):
            return self.app(environ, start_response)

        _wsgi_middleware_applied.set(True)
        try:
            hub = Hub(Hub.current)

            with hub:
                with capture_internal_exceptions():
                    with hub.configure_scope() as scope:
                        scope.clear_breadcrumbs()
                        scope._name = "wsgi"
                        scope.add_event_processor(_make_wsgi_event_processor(environ))

                span = Span.continue_from_environ(environ)
                span.op = "http.server"
                span.transaction = "generic WSGI request"

                with hub.start_span(span) as span:
                    try:
                        rv = self.app(
                            environ,
                            functools.partial(
                                _sentry_start_response, start_response, span
                            ),
                        )
                    except BaseException:
                        reraise(*_capture_exception(hub))
        finally:
            _wsgi_middleware_applied.set(False)

        return _ScopedResponse(hub, rv)