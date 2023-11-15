def main(*args, **kwargs):
    warnings.warn(
        '`sphinx.apidoc.main()` has moved to `sphinx.ext.apidoc.main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    args = args[1:]  # skip first argument to adjust arguments (refs: #4615)
    _main(*args, **kwargs)