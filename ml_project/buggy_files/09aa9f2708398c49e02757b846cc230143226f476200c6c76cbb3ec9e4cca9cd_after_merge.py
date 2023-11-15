    def _emit(self, record):
        # type: (LogRecord) -> None
        if not _can_record(record):
            return

        hub = Hub.current
        if hub.client is None:
            return

        client_options = hub.client.options

        # exc_info might be None or (None, None, None)
        #
        # exc_info may also be any falsy value due to Python stdlib being
        # liberal with what it receives and Celery's billiard being "liberal"
        # with what it sends. See
        # https://github.com/getsentry/sentry-python/issues/904
        if record.exc_info and record.exc_info[0] is not None:
            event, hint = event_from_exception(
                record.exc_info,
                client_options=client_options,
                mechanism={"type": "logging", "handled": True},
            )
        elif record.exc_info and record.exc_info[0] is None:
            event = {}
            hint = {}
            with capture_internal_exceptions():
                event["threads"] = {
                    "values": [
                        {
                            "stacktrace": current_stacktrace(
                                client_options["with_locals"]
                            ),
                            "crashed": False,
                            "current": True,
                        }
                    ]
                }
        else:
            event = {}
            hint = {}

        hint["log_record"] = record

        event["level"] = _logging_to_event_level(record.levelname)
        event["logger"] = record.name
        event["logentry"] = {"message": to_string(record.msg), "params": record.args}
        event["extra"] = _extra_from_record(record)

        hub.capture_event(event, hint=hint)