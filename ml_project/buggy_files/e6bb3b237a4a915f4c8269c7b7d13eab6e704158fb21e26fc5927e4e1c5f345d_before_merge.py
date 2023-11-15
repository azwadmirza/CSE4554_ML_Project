def _wrap_task_call(f):
    # Need to wrap task call because the exception is caught before we get to
    # see it. Also celery's reported stacktrace is untrustworthy.
    def _inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            reraise(*_capture_exception())

    return _inner