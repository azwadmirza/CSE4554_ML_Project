def main(*args, **kwargs):
    warnings.warn(
        '`sphinx.apidoc.main()` has moved to `sphinx.ext.apidoc.main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    _main(*args, **kwargs)