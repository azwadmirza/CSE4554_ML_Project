def hy_exc_handler(exc_type, exc_value, exc_traceback):
    """A `sys.excepthook` handler that uses `hy_exc_filter` to
    remove internal Hy frames from a traceback print-out.
    """
    if os.environ.get('HY_DEBUG', False):
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)

    try:
        output = hy_exc_filter(exc_type, exc_value, exc_traceback)
        sys.stderr.write(output)
        sys.stderr.flush()
    except Exception:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)