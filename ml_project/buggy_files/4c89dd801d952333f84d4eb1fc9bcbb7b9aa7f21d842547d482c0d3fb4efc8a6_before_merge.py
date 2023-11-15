def main(*args, **kwargs):
    from .cmd import build
    warnings.warn(
        '`sphinx.main()` has moved to `sphinx.cmd.build.main()`.',
        RemovedInSphinx20Warning,
        stacklevel=2,
    )
    return build.main(*args, **kwargs)