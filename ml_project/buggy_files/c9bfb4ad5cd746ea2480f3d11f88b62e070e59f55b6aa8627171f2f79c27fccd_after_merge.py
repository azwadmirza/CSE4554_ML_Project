def make_main(argv=sys.argv):
    """Sphinx build "make mode" entry."""
    from .cmd import build
    warnings.warn(
        '`sphinx.build_main()` has moved to `sphinx.cmd.build.make_main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    return build.make_main(argv[1:])  # skip first argument to adjust arguments (refs: #4615)