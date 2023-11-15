def print_version_and_date():
    """\
    Useful for starting a notebook so you see when you started working.
    """
    from . import __version__
    from ._settings import settings
    print(
        f'Running Scanpy {__version__}, '
        f'on {datetime.now():%Y-%m-%d %H:%M}.',
        file=settings.logfile,
    )