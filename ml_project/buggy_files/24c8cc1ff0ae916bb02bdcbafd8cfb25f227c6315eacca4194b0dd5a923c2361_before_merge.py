def print_versions(*, file=None):
    """Print print versions of imported packages"""
    if file is None:  # Inform people about the behavior change
        warning('If you miss a compact list, please try `print_header`!')
    stdout = sys.stdout
    try:
        buf = sys.stdout = io.StringIO()
        sinfo(dependencies=True)
    finally:
        sys.stdout = stdout
    output = buf.getvalue()
    print(output, file=file)