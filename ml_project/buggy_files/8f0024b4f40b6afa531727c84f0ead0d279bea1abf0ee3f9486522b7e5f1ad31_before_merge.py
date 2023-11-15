def main(*args, **kwargs):
    warnings.warn(
        '`sphinx.quickstart.main()` has moved to `sphinx.cmd.quickstart.'
        'main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    _main(*args, **kwargs)