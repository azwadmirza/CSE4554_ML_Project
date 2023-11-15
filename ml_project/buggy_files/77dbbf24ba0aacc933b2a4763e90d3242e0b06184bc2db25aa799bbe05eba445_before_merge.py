def _wrap_run(parent_hub, old_run):
    def run(*a, **kw):
        hub = parent_hub or Hub.current

        with hub:
            try:
                return old_run(*a, **kw)
            except Exception:
                reraise(*_capture_exception())

    return run