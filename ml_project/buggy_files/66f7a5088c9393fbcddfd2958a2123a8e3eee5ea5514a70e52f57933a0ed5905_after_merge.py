def print_version_and_date(*, file=None):
    """\
    Useful for starting a notebook so you see when you started working.
    """
    from . import __version__
    if file is None:
        file = sys.stdout
    print(
        f'Running Scanpy {__version__}, '
        f'on {datetime.now():%Y-%m-%d %H:%M}.',
        file=file,
    )