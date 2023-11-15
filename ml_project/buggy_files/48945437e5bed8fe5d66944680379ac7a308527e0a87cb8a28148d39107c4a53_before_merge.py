    def _inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            reraise(*_capture_exception())