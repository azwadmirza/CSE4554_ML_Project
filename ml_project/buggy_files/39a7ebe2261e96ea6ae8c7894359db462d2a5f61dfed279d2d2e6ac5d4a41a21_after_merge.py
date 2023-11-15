def print_versions(*, file=None):
    """Print print versions of imported packages"""
    if file is None:
        sinfo(dependencies=True)
    else:
        stdout = sys.stdout
        try:
            sys.stdout = file
            sinfo(dependencies=True)
        finally:
            sys.stdout = stdout