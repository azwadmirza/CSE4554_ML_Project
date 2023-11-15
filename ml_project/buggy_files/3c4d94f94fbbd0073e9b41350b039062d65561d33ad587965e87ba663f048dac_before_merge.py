def _build_docstring():
    global __doc__
    from . import subcommands

    for cls in subcommands.all:
        __doc__ += "%8s : %s\n" % (cls.name, cls.help)