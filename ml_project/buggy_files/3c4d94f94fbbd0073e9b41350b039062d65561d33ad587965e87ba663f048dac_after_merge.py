def _build_docstring():
    global __doc__
    from . import subcommands

    for cls in subcommands.all:
        # running python with -OO will discard docstrings -> __doc__ is None
        if __doc__ is None:
            __doc__ = ''
        __doc__ += "%8s : %s\n" % (cls.name, cls.help)