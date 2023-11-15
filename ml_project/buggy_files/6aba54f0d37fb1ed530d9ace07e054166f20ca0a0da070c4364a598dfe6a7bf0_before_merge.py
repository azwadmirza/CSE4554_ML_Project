def build_main(argv=sys.argv):
    """Sphinx build "main" command-line entry."""
    warnings.warn(
        '`sphinx.build_main()` has moved to `sphinx.cmd.build.build_main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    return build.build_main(argv[1:])  # skip first argument to adjust arguments (refs: #4615)