def _make_event_processor(task, uuid, args, kwargs, request=None):
    def event_processor(event, hint):
        with capture_internal_exceptions():
            event["transaction"] = task.name

        with capture_internal_exceptions():
            extra = event.setdefault("extra", {})
            extra["celery-job"] = {
                "task_name": task.name,
                "args": args,
                "kwargs": kwargs,
            }

        if "exc_info" in hint:
            with capture_internal_exceptions():
                if isinstance(hint["exc_info"][1], Retry):
                    return None

                if hasattr(task, "throws") and isinstance(
                    hint["exc_info"][1], task.throws
                ):
                    return None

            with capture_internal_exceptions():
                if issubclass(hint["exc_info"][0], SoftTimeLimitExceeded):
                    event["fingerprint"] = [
                        "celery",
                        "SoftTimeLimitExceeded",
                        getattr(task, "name", task),
                    ]

        return event

    return event_processor