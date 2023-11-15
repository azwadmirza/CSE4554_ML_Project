def console_encode(value):
    if py3compat.PY3 or not isinstance(value, unicode):
        return value

    try:
        import sys
        return value.encode(sys.stdin.encoding or 'utf-8', 'replace')
    except (AttributeError, TypeError):
        return value.encode('ascii', 'replace')