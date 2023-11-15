def sys_stdout_write_wrapper(s, stream=sys.stdout):
    """Python 2.6 chokes on unicode being passed to sys.stdout.write.

    This is an adapter because PY2 is ok with bytes and PY3 requires text.
    """
    assert type(s) is five.text
    if five.PY2:  # pragma: no cover (PY2)
        s = s.encode('UTF-8')
    stream.write(s)