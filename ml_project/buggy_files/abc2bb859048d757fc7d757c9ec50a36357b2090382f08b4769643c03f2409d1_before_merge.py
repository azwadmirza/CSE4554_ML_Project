    def emit(self, record):
        # type: (ExceptionReporter) -> None
        try:
            request = record.request  # type: HttpRequest

            exception_filter = get_exception_reporter_filter(request)

            if record.exc_info:
                stack_trace = ''.join(traceback.format_exception(*record.exc_info))  # type: Optional[str]
            else:
                stack_trace = None

            try:
                user_profile = request.user
                user_full_name = user_profile.full_name
                user_email = user_profile.email
            except Exception:
                traceback.print_exc()
                # Error was triggered by an anonymous user.
                user_full_name = None
                user_email = None

            try:
                data = request.GET if request.method == 'GET' else \
                    exception_filter.get_post_parameters(request)
            except Exception:
                # exception_filter.get_post_parameters will throw
                # RequestDataTooBig if there's a really big file uploaded
                data = {}

            try:
                host = request.get_host().split(':')[0]
            except Exception:
                # request.get_host() will throw a DisallowedHost
                # exception if the host is invalid
                host = platform.node()

            report = dict(
                node = platform.node(),
                host = host,
                method = request.method,
                path = request.path,
                data = data,
                remote_addr = request.META.get('REMOTE_ADDR', None),
                query_string = request.META.get('QUERY_STRING', None),
                server_name = request.META.get('SERVER_NAME', None),
                message = record.getMessage(),
                stack_trace = stack_trace,
                user_full_name = user_full_name,
                user_email = user_email,
            )
        except Exception:
            traceback.print_exc()
            report = dict(
                node = platform.node(),
                host = platform.node(),
                message = record.getMessage(),
            )

        try:
            if settings.STAGING_ERROR_NOTIFICATIONS:
                # On staging, process the report directly so it can happen inside this
                # try/except to prevent looping
                from zilencer.error_notify import notify_server_error
                notify_server_error(report)
            else:
                queue_json_publish('error_reports', dict(
                    type = "server",
                    report = report,
                ), lambda x: None)
        except Exception:
            # If this breaks, complain loudly but don't pass the traceback up the stream
            # However, we *don't* want to use logging.exception since that could trigger a loop.
            logging.warning("Reporting an exception triggered an exception!", exc_info=True)